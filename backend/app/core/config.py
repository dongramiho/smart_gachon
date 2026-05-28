import logging
import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    PROJECT_NAME: str = "News-based Stock Red Flag Detection API"
    PROJECT_VERSION: str = "1.1.0"

    NAVER_CLIENT_ID: str = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET: str = os.getenv("NAVER_CLIENT_SECRET", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./redflag.db")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

    # LLM (optional)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "").lower()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")

    def validate(self) -> None:
        if not self.JWT_SECRET:
            raise RuntimeError(
                "JWT_SECRET 환경변수가 설정되지 않았습니다. "
                "강력한 랜덤 시크릿을 설정하세요: "
                "python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(self.JWT_SECRET) < 32:
            logger.warning("JWT_SECRET이 32자 미만입니다. 프로덕션에서는 더 긴 시크릿을 사용하세요.")


settings = Settings()
