from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain_litellm import ChatLiteLLM
from pydantic import BaseModel

from chatwilly_backend.settings import global_settings
from chatwilly_backend.tools import ALL_TOOLS

guardrails_model = ChatLiteLLM(
    model=global_settings.guardrail_model.model_name,
    base_url=global_settings.guardrail_model.base_url,
    api_key=global_settings.guardrail_model.api_key,
    temperature=global_settings.guardrail_model.temperature,
    max_tokens=global_settings.guardrail_model.max_tokens,
    timeout=30,
)


class GuardrailResult(BaseModel):
    passed: bool


guardrails_agent = create_agent(
    guardrails_model,
    tools=[],
    system_prompt=global_settings.guardrail_model.system_prompt,
    response_format=GuardrailResult,
)

response_model = ChatLiteLLM(
    model=global_settings.response_agent_model.model_name,
    base_url=global_settings.response_agent_model.base_url,
    api_key=global_settings.response_agent_model.api_key,
    temperature=global_settings.response_agent_model.temperature,
    max_tokens=global_settings.response_agent_model.max_tokens,
    timeout=30,
    streaming=True,
)
response_agent = create_agent(
    response_model,
    tools=ALL_TOOLS,
    system_prompt=global_settings.response_agent_model.system_prompt,
    middleware=[
        ModelCallLimitMiddleware(
            run_limit=global_settings.response_agent_model.max_iterations,
            exit_behavior="end",
        ),
    ],
)
