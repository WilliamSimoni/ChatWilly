from chatwilly_knowledge.settings import knowledge_settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

extractor_model = ChatOpenAI(
    model=knowledge_settings.extractor_model.model_name,
    base_url=knowledge_settings.extractor_model.base_url,
    api_key=knowledge_settings.extractor_model.api_key,
    temperature=knowledge_settings.extractor_model.temperature,
    max_tokens=knowledge_settings.extractor_model.max_tokens,
    timeout=30,
)

embeddings_model = OpenAIEmbeddings(
    model=knowledge_settings.embedding_model.model_name,
    base_url=knowledge_settings.embedding_model.base_url,
    api_key=knowledge_settings.embedding_model.api_key,
    check_embedding_ctx_length=False,
)
