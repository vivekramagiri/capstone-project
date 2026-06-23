import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4.6")
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    # FastAPI
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_LOG_LEVEL: str = os.getenv("API_LOG_LEVEL", "INFO")

    # Streamlit
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # MCP Servers
    APPLICANT_DB_PORT: int = int(os.getenv("APPLICANT_DB_PORT", "8100"))
    RISK_RULES_PORT: int = int(os.getenv("RISK_RULES_PORT", "8101"))
    DECISION_SYNTHESIS_PORT: int = int(os.getenv("DECISION_SYNTHESIS_PORT", "8102"))
    NOTIFICATION_SYSTEM_PORT: int = int(os.getenv("NOTIFICATION_SYSTEM_PORT", "8103"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # API Keys Validation
    @classmethod
    def validate(cls) -> bool:
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return True


settings = Settings()
