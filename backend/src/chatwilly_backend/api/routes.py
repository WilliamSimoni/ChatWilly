from chatwilly_backend.api.rate_limit import RateLimit
from chatwilly_backend.settings import global_settings
from fastapi import APIRouter, Request, HTTPException
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from chatwilly_backend.api.route_models import ChatRequest
from chatwilly_backend.graph import agent 
import json

router = APIRouter()

@router.post(
    "/chat",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "Server-Sent Events stream"
        }
    },
    dependencies=[Depends(RateLimit(global_settings.rate_limit_timeout))],
)
async def chat_endpoint(body: ChatRequest):

    if not body.messages:
        raise HTTPException(status_code=400, detail="La lista messaggi è vuota.")

    formatted_messages =[msg.model_dump() for msg in body.messages]

    async def event_generator():
        try:
            async for event in agent.astream_events(
                {"messages": formatted_messages}, 
                version="v2"
            ):
                kind = event["event"]
                metadata = event["metadata"]
                
                if kind == "on_chat_model_stream":
                    node_name = metadata.get("langgraph_node")
                    checkpoint_ns = metadata.get("checkpoint_ns", "")

                    if node_name == "model" and "response_generation" in checkpoint_ns:
                        content = event["data"]["chunk"].content
                        if content:
                            data = json.dumps({"content": content})
                            yield f"data: {data}\n\n"
                            
                elif kind == "on_chain_end" and event["name"] == "guardrail_block":
                    output = event["data"].get("output", {})
                    if "messages" in output and output["messages"]:
                        content = output["messages"][-1].content
                        data = json.dumps({"content": content})
                        yield f"data: {data}\n\n"

            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
    
@router.get("/settings")
async def get_settings():
    """
    Returns the current application settings.
    Sensitive fields (like API keys and Database URLs) are excluded.
    """
    return global_settings.model_dump()