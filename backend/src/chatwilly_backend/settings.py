import os
from pathlib import Path
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from chatwilly_backend.prompt.input_guardrail_prompt import (
    INPUT_GUARDRAIL_SYSTEM_PROMPT,
)
from chatwilly_backend.prompt.response_agent_prompt import RESPONSE_AGENT_SYSTEM_PROMPT

BACKEND_ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = os.getenv("CONFIG_PATH", BACKEND_ROOT_DIR / "config.yaml")
ENV_PATH = os.getenv("ENV_PATH", BACKEND_ROOT_DIR / ".env")


class RedisConfig(BaseModel):
    enabled: bool = False
    url: str = "redis://localhost:6379"


class AIModelConfig(BaseModel):
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0


class EmbeddingModelConfig(BaseModel):
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    model_name: str = "text-embedding-3-small"


class GuardrailConfig(AIModelConfig):
    system_prompt: str = INPUT_GUARDRAIL_SYSTEM_PROMPT


class AgentConfig(AIModelConfig):
    system_prompt: str = RESPONSE_AGENT_SYSTEM_PROMPT
    max_iterations: int = 5


class QdrantConfig(BaseModel):
    url: str = "http://localhost:6333"
    api_key: str | None = None
    collection_name: str = "chatwilly_brain"
    vector_size: int = 1536


class Settings(BaseSettings):
    """
    Loads configuration from config.yaml and allows override via environment variables.
    Precedence (highest to lowest):
      1. Environment variables (e.g. DATABASE__REDIS_URL)
      2. Values in config.yaml
      3. Hardcoded default values
    """

    app_name: str = "ChatWilly"
    app_version: str = "0.1.0"
    app_port: int = 8000

    # rate limit settings
    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 60
    rate_limit_timeout: int = 10

    # Map the nested configuration
    redis: RedisConfig = RedisConfig()
    qdrant: QdrantConfig = QdrantConfig()

    # Root level configurations
    debug: bool = False

    guardrail_model: GuardrailConfig = GuardrailConfig()
    response_agent_model: AgentConfig = AgentConfig()
    embedding_model: EmbeddingModelConfig = EmbeddingModelConfig()

    # Configure Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        yaml_file=CONFIG_PATH,
        yaml_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the sources and their precedence.
        The first item in the tuple has the highest precedence.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
        )


global_settings = Settings()
