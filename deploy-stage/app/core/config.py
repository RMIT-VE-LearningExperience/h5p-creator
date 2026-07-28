from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    default_ai_provider: str = "val"
    val_api_key: str | None = None
    val_base_url: str = "https://val-npe.rmit.edu.au/api"
    val_model: str = "openai-gpt-5.4"
    canvas_base_url: str | None = None
    canvas_api_token: str | None = None
    canvas_account_id: str | None = None
    canvas_allowed_hosts: str | None = None
    canvas_course_search_ids: str | None = None
    youtube_api_key: str | None = None
    youtube_transcript_webshare_username: str | None = None
    youtube_transcript_webshare_password: str | None = None
    youtube_transcript_proxy_url: str | None = None
    powerpoint_template_path: str = "app/templates/PowerPoint_Template_Showcase.pptx"
    upload_dir: str = "/tmp/h5p-creator/uploads"
    output_dir: str = "/tmp/h5p-creator/outputs"


settings = Settings()
