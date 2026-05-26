import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("redflag.startup")

from app.api.analyze_router import router as analyze_router
from app.api.auth_router import router as auth_router
from app.api.community_router import router as community_router
from app.api.news_router import router as news_router
from app.api.report_router import router as report_router
from app.api.watchlist_router import router as watchlist_router
from app.core.config import settings
from app.database.session import init_db


def _warmup_finbert() -> None:
    """ENABLE_FINBERT=true 일 때 백그라운드에서 KR/EN 파이프라인을 미리 다운로드·로드.
    시연 시 첫 요청에서 모델 로딩으로 5~30초 대기하는 일을 막는다."""
    from app.ai.finbert_analyzer import finbert_analyzer

    try:
        finbert_analyzer.analyze("warmup")           # EN 파이프라인
        finbert_analyzer.analyze("워밍업")             # KR 파이프라인
        logger.info("FinBERT warmup complete (EN+KR pipelines ready)")
    except Exception as exc:  # noqa: BLE001 — 워밍업 실패가 서버를 죽이면 안 됨
        logger.warning("FinBERT warmup failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.ENABLE_FINBERT:
        # 별도 스레드에 띄워야 startup이 막히지 않음 — 첫 분석 요청은 워밍 완료를 기다림.
        asyncio.get_running_loop().run_in_executor(None, _warmup_finbert)
        logger.info("FinBERT warmup dispatched (running in background)")
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(news_router)
app.include_router(report_router)
app.include_router(community_router)
app.include_router(watchlist_router)


@app.get("/")
def root():
    return {
        "message": "News-based Stock Red Flag Detection API is running.",
        "version": settings.PROJECT_VERSION,
    }
