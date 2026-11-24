"""Configuration management for BaseInt."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default=f"sqlite:///{BASE_DIR / 'baseint_analytics.db'}",
        validation_alias="DATABASE_URL",
    )

    # LLM Settings
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", validation_alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.0, validation_alias="LLM_TEMPERATURE")

    # Safety & Reflection Controls
    max_retries: int = Field(default=3, validation_alias="MAX_RETRIES")
    execution_timeout_seconds: int = Field(default=15, validation_alias="EXECUTION_TIMEOUT_SECONDS")
    ast_enforce_read_only: bool = Field(default=True, validation_alias="AST_ENFORCE_READ_ONLY")
    nemo_guardrails_enabled: bool = Field(default=True, validation_alias="NEMO_GUARDRAILS_ENABLED")

    # Networking & Ports
    streamlit_server_port: int = Field(default=8501, validation_alias="STREAMLIT_SERVER_PORT")
    docs_server_port: int = Field(default=3000, validation_alias="DOCS_SERVER_PORT")
    base_url: str = Field(default="http://localhost:3000", validation_alias="BASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

