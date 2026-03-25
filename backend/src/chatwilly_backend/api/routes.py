import json
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from fastapi.responses import StreamingResponse

from chatwilly_backend.api.auth import (
    create_conversation_token,
    get_conversation_id,
    verify_turnstile,
)
from chatwilly_backend.api.rate_limit import RateLimit
from chatwilly_backend.api.route_models import (
    ChatRequest,
    ConversationStartEvent,
    DoneEvent,
    GuardrailBlockEvent,
    MessageChunkEvent,
    ToolCallEvent,
)
from chatwilly_backend.settings import global_settings

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/token",
    dependencies=[Depends(RateLimit(global_settings.rate_limit_timeout))],
)
async def issue_token(request: Request):
    """
    Issues a signed JWT with a fresh conversation_id.
    Requires a valid Cloudflare Turnstile token in the header.
    """
    turnstile_token = request.headers.get("X-Turnstile-Token", "")
    await verify_turnstile(turnstile_token)
    return {"token": create_conversation_token()}


@router.post(
    "/chat",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "Server-Sent Events stream",
        }
    },
    dependencies=[Depends(RateLimit(global_settings.rate_limit_timeout))],
)
async def chat_endpoint(
    body: ChatRequest,
    request: Request,
    conversation_id: str = Depends(get_conversation_id),
):
    if not body.message:
        raise HTTPException(status_code=400, detail="Empty message")

    agent = request.app.state.agent
    config = {"configurable": {"thread_id": conversation_id}}
    new_message = body.message.model_dump()

    async def event_generator():
        start_event = ConversationStartEvent(conversation_id=conversation_id)
        yield f"data: {start_event.model_dump_json()}\n\n"

        try:
            async for event in agent.astream_events(
                {"messages": [new_message]},
                config=config,
                version="v2",
            ):
                if await request.is_disconnected():
                    break

                kind = event["event"]
                metadata = event["metadata"]
                node_name = metadata.get("langgraph_node")
                checkpoint_ns = metadata.get("checkpoint_ns", "")

                event_model = None

                if kind == "on_chat_model_stream":
                    if node_name == "model" and "response_generation" in checkpoint_ns:
                        content = event["data"]["chunk"].content
                        if content:
                            event_model = MessageChunkEvent(content=content)

                elif kind == "on_chain_end" and event["name"] == "guardrail_block":
                    output = event["data"].get("output", {})
                    if "messages" in output and output["messages"]:
                        content = output["messages"][-1].content
                        event_model = GuardrailBlockEvent(content=content)

                elif kind == "on_tool_start":
                    if node_name == "tools" and "response_generation" in checkpoint_ns:
                        event_model = ToolCallEvent(name=event["name"])

                if event_model:
                    yield f"data: {event_model.model_dump_json()}\n\n"

            done_event = DoneEvent()
            yield f"data: {done_event.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
