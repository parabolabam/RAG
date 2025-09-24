import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

import debugpy
import uvicorn

from senpy_ai_news_report.features.news.router import router as news_router
from senpy_ai_news_report.utils.auth import require_api_token

load_dotenv()

if os.getenv("DEBUG") is not None:
    debugpy.listen(5679)

app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight": False},
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(news_router)


@app.get("/openapi.json", include_in_schema=False)
async def openapi_endpoint(_: None = Depends(require_api_token)) -> JSONResponse:
    return JSONResponse(app.openapi())


@app.get("/docs", include_in_schema=False)
async def swagger_ui(_: None = Depends(require_api_token)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Senpy AI News API")


if __name__ == "__main__":
    uvicorn.run(
        "senpy_ai_news_report.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
