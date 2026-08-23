import os
from typing import List

class Settings:
    PROJECT_NAME: str = "Voice Command Shopping Assistant"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shopping_assistant.db")
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    ENABLE_AI_PARSER: bool = os.getenv("ENABLE_AI_PARSER", "true").lower() in ("true", "1", "yes")
    ENABLE_AI_RESPONSES: bool = os.getenv("ENABLE_AI_RESPONSES", "true").lower() in ("true", "1", "yes")

settings = Settings()
