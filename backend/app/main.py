import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.analyze_router import router as analyze_router
from app.api.auth_router import router as auth_router
from app.api.news_router import router as news_router
from app.api.report_router import router as report_router
from app.core.config import settings
from app.core.limiter import limiter
from app.database.session import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate()
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        "A FastAPI backend for detecting corporate red flags from financial news "
        "using FinBERT sentiment analysis, rule-based risk scoring, and "
        "LLM-compatible explanation generation."
    ),
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(news_router)
app.include_router(report_router)


@app.get("/")
def root():
    return {
        "message": "News-based Stock Red Flag Detection API is running.",
        "version": settings.PROJECT_VERSION,
    }
