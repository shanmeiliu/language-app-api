import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = "Language App API"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    database_url: str | None = os.getenv("DATABASE_URL")

settings = Settings()