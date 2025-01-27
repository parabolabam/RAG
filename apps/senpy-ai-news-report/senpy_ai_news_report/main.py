import uvicorn
from fastapi import FastAPI
from senpy_ai_chatbot.features.news.router import router as news_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

app.include_router(news_router)

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run("senpy_ai_chatbot.main:app", host="0.0.0.0", port=8000, reload=True)
