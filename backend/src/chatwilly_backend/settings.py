from pathlib import Path
from typing import Tuple, Type
import os

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

BACKEND_ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = os.getenv("CONFIG_PATH", BACKEND_ROOT_DIR / "config.yaml")
ENV_PATH = os.getenv("ENV_PATH", BACKEND_ROOT_DIR / ".env")

class DatabaseConfig(BaseModel):
    redis_url: str = "redis://localhost:6379"
    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 60

class AIModelConfig(BaseModel):
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0

class GuardrailConfig(AIModelConfig):
    system_prompt: str ="""
You are a helpful assistant that checks whether the user's input is related to the professional profile of ChatWilly, including work experience, skills, and projects.

Set `passed` to true if the input is relevant to the professional profile.
Set `passed` to false if it is not relevant.
"""

class AgentConfig(AIModelConfig):
    system_prompt: str = "You are ChatWilly, a professional AI assistant that can answer questions about your work experience, skills, and projects. Use the provided tools to fetch information when necessary. Always provide accurate and concise answers based on your professional profile."
    max_iterations: int = 5

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

    # Map the nested configuration
    database: DatabaseConfig = DatabaseConfig()
    
    # Root level configurations
    debug: bool = False
    
    guardrail_model: GuardrailConfig = GuardrailConfig()
    response_agent_model: AgentConfig = AgentConfig()

    # Configure Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        yaml_file=CONFIG_PATH,
        yaml_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
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