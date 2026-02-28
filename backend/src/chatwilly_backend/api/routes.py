from chatwilly_backend.settings import global_settings
from fastapi import APIRouter, Request, HTTPException
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
    }
)
async def chat_endpoint(request: Request, body: ChatRequest):

    if not body.messages:
        raise HTTPException(status_code=400, detail="La lista messaggi è vuota.")

    formatted_messages =[msg.model_dump() for msg in body.messages]

    async def event_generator():
        try:
            # version="v2" is required for the modern LangChain events API
            async for event in agent.astream_events(
                {"messages": formatted_messages}, 
                version="v2"
            ):
                kind = event["event"]
                metadata = event["metadata"]
                
                # 1. Stream tokens from the response LLM
                if kind == "on_chat_model_stream":
                    # Filter: Only yield tokens if the current active node is "response_generation".
                    # This prevents streaming the "guardrail_input" agent's internal thought process!
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    checkpoint_ns = metadata.get("checkpoint_ns", "")

                    if node_name == "model" and "response_generation" in checkpoint_ns:
                        content = event["data"]["chunk"].content
                        if content:
                            # It's best practice to JSON encode SSE data so newlines 
                            # don't break the Server-Sent Event formatting.
                            data = json.dumps({"content": content})
                            yield f"data: {data}\n\n"
                            
                # 2. Handle the guardrail block
                # Because it's a static function and doesn't use an LLM, it won't trigger `on_chat_model_stream`.
                # We catch its completion event instead.
                elif kind == "on_chain_end" and event["name"] == "guardrail_block":
                    output = event["data"].get("output", {})
                    if "messages" in output and output["messages"]:
                        # Extract the static AIMessage content we set in graph.py
                        content = output["messages"][-1].content
                        data = json.dumps({"content": content})
                        yield f"data: {data}\n\n"

            # Optional but recommended: Send a standard DONE signal when generation finishes
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            # Yield an error cleanly to the frontend if something fails during streaming
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