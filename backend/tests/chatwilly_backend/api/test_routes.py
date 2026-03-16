from unittest.mock import AsyncMock, patch

import pytest
from chatwilly_backend.api.route_models import (
    DoneEvent,
    GuardrailBlockEvent,
    MessageChunkEvent,
    ToolCallEvent,
)
from chatwilly_backend.api.routes import router
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(router)

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_rate_limit():
    """
    Automatically mock the RateLimit dependency for all tests to prevent
    Redis/in-memory rate limiting issues during unit testing.
    """
    with patch(
        "chatwilly_backend.api.rate_limit.RateLimit.__call__", new_callable=AsyncMock
    ) as mock:
        yield mock


class MockChunk:
    def __init__(self, content):
        self.content = content


class MockMessage:
    def __init__(self, content):
        self.content = content


def test_chat_endpoint_empty_messages():
    """
    Test that sending an empty messages list raises an HTTP 400 exception.
    """
    payload = {"messages": []}
    response = client.post("/chat", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "La lista messaggi è vuota."}


@patch("chatwilly_backend.api.routes.agent")
def test_chat_endpoint_model_stream(mock_agent):
    """
    Test a normal chat completion streaming (on_chat_model_stream).
    """

    # This part that mocks the agent's raw output remains the same
    async def mock_stream(*args, **kwargs):
        yield {
            "event": "on_chat_model_stream",
            "metadata": {
                "langgraph_node": "model",
                "checkpoint_ns": "some_ns:response_generation:other_ns",
            },
            "data": {"chunk": MockChunk("Hello")},
        }
        yield {
            "event": "on_chat_model_stream",
            "metadata": {
                "langgraph_node": "model",
                "checkpoint_ns": "some_ns:response_generation:other_ns",
            },
            "data": {"chunk": MockChunk(" World!")},
        }

    mock_agent.astream_events = mock_stream

    payload = {"messages": [{"role": "user", "content": "Hi"}]}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    text = response.text

    expected_chunk1 = MessageChunkEvent(content="Hello").model_dump_json()
    expected_chunk2 = MessageChunkEvent(content=" World!").model_dump_json()
    expected_done = DoneEvent().model_dump_json()

    assert f"data: {expected_chunk1}\n\n" in text
    assert f"data: {expected_chunk2}\n\n" in text
    assert f"data: {expected_done}\n\n" in text


@patch("chatwilly_backend.api.routes.agent")
def test_chat_endpoint_tool_call(mock_agent):
    """
    Test that an on_tool_start event is correctly streamed as a ToolCallEvent.
    """

    async def mock_stream(*args, **kwargs):
        yield {
            "event": "on_tool_start",
            "name": "search_work_experience_and_projects",
            "metadata": {
                "langgraph_node": "tools",
                "checkpoint_ns": "prefix:response_generation:suffix",
            },
            "data": {"input": {"query": "fondazione startup"}},
        }

    mock_agent.astream_events = mock_stream

    payload = {"messages": [{"role": "user", "content": "Tell me about startups"}]}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    expected_event = ToolCallEvent(
        name="search_work_experience_and_projects"
    ).model_dump_json()
    expected_done = DoneEvent().model_dump_json()

    assert f"data: {expected_event}\n\n" in response.text
    assert f"data: {expected_done}\n\n" in response.text


@patch("chatwilly_backend.api.routes.agent")
def test_chat_endpoint_guardrail_block(mock_agent):
    """
    Test that if a guardrail triggers, the appropriate message is streamed.
    """

    async def mock_stream(*args, **kwargs):
        yield {
            "event": "on_chain_end",
            "name": "guardrail_block",
            "metadata": {},
            "data": {"output": {"messages": [MockMessage("Blocked by guardrail.")]}},
        }

    mock_agent.astream_events = mock_stream

    payload = {"messages": [{"role": "user", "content": "bad prompt"}]}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    text = response.text

    expected_event = GuardrailBlockEvent(
        content="Blocked by guardrail."
    ).model_dump_json()
    expected_done = DoneEvent().model_dump_json()

    assert f"data: {expected_event}\n\n" in text
    assert f"data: {expected_done}\n\n" in text


@patch("chatwilly_backend.api.routes.logger")
@patch("chatwilly_backend.api.routes.agent")
def test_chat_endpoint_exception_handling(mock_agent, mock_logger):
    """
    Test that exceptions during the stream generation are caught,
    logged, and streamed back as a JSON error.
    """

    async def mock_stream_error(*args, **kwargs):
        if True:
            raise ValueError("Something went terribly wrong.")
        yield {}

    mock_agent.astream_events = mock_stream_error

    payload = {"messages": [{"role": "user", "content": "trigger error"}]}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    mock_logger.error.assert_called_once()
