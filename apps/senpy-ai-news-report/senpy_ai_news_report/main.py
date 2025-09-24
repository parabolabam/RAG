import logging
import os
from contextlib import asynccontextmanager

import debugpy
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

from crons.scheduler import ensure_scheduler_started, shutdown_scheduler
from senpy_ai_news_report.features.cron.router import router as cron_router
from senpy_ai_news_report.features.news.router import router as news_router

load_dotenv()

logger = logging.getLogger(__name__)

if os.getenv("DEBUG") is not None:
    debugpy.listen(5679)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await ensure_scheduler_started()
        logger.info("Cron scheduler started")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to start cron scheduler: %s", exc)
    try:
        yield
    finally:
        await shutdown_scheduler(wait=True)


app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight": False},
    lifespan=lifespan,
)

app.include_router(news_router)
app.include_router(cron_router)


if __name__ == "__main__":
    uvicorn.run(
        "senpy_ai_news_report.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
