from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    default_ai_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-2024-08-06"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-1"
    val_api_key: str | None = None
    val_base_url: str = "https://val-sandbox.rmit.edu.au/api"
    val_model: str = "openai-gpt-4o-mini"
    upload_dir: str = "/tmp/h5p-creator/uploads"
    output_dir: str = "/tmp/h5p-creator/outputs"


settings = Settings()
