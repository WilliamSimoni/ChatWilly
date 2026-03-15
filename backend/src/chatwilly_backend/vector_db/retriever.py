import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from tenacity import retry, stop_after_attempt, wait_exponential

from chatwilly_backend.settings import global_settings

from .embedding import embeddings_model

logger = logging.getLogger(__name__)

qdrant = AsyncQdrantClient(
    url=global_settings.qdrant.url, api_key=global_settings.qdrant.api_key
)

COLLECTION_NAME = global_settings.qdrant.collection_name


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def execute_qdrant_query(query: str, category: str, limit: int) -> str:
    """
    Inner function that actually performs the API calls.
    Protected by tenacity retries.
    """
    query_vector = await embeddings_model.aembed_query(query)

    search_response = await qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="category", match=models.MatchValue(value=category)
                )
            ]
        ),
        limit=limit,
        with_payload=True,
    )

    hits = search_response.points

    if not hits:
        return f"No results found in category '{category}' for the query: '{query}'. Try using different keywords."

    formatted_chunks = []
    for i, hit in enumerate(hits, 1):
        payload = hit.payload
        summary = payload.get("document_summary", "")
        text = payload.get("text", "")

        chunk_str = (
            f"[RESULT {i}]\nProject Context: {summary}\nNarrative Detail: {text}\n"
        )
        formatted_chunks.append(chunk_str)

    return "\n---\n".join(formatted_chunks)


def vector_search(query: str, category: str, limit: int = 10) -> str:
    """
    Wrapper function called by the tools.
    If all retries fail, it catches the exception and instructs the LLM on how to behave.
    """
    try:
        return execute_qdrant_query(query, category, limit)
    except Exception as e:
        logger.error(f"Vector search failed after retries for query '{query}': {e}")
        return (
            "SYSTEM WARNING: The memory database is currently unavailable due to technical issues. "
            "DO NOT attempt to use other search tools. "
            "Gracefully inform the user that you are experiencing temporary 'memory loss' or technical difficulties, "
            "and try to answer the question using the knowledge you already have in the current conversation."
        )
