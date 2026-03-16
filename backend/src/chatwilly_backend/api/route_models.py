from typing import Literal, Optional, Union

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: ChatMessage
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str


class MessageChunkEvent(BaseModel):
    type: Literal["message_chunk"] = "message_chunk"
    content: str


class ConversationStartEvent(BaseModel):
    type: Literal["conversation_start"] = "conversation_start"
    conversation_id: str


class ToolCallEvent(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    name: str


class GuardrailBlockEvent(BaseModel):
    type: Literal["guardrail_block"] = "guardrail_block"
    content: str


class DoneEvent(BaseModel):
    type: Literal["done"] = "done"


StreamEvent = Union[
    ConversationStartEvent,
    MessageChunkEvent,
    ToolCallEvent,
    GuardrailBlockEvent,
    DoneEvent,
]
