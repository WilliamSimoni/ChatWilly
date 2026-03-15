from langchain_openai import OpenAIEmbeddings

from chatwilly_backend.settings import global_settings

embeddings_model = OpenAIEmbeddings(
    model=global_settings.embedding_model.model_name,
    base_url=global_settings.embedding_model.base_url,
    api_key=global_settings.embedding_model.api_key,
    check_embedding_ctx_length=False,
)
