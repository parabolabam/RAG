import uvicorn
import os
from fastapi import FastAPI
from senpy_ai_chatbot.features.send_channel_message import send_message_to_channel
from senpy_ai_chatbot.features.news.router import router as news_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

app.include_router(news_router)


@app.post("/send-message")
async def send_test_message():
    await send_message_to_channel(
        int(os.getenv("TELEGRAM_CHANNEL_ID") or -1), "Hello! 😛"
    )


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run("senpy_ai_chatbot.main:app", host="0.0.0.0", port=8000, reload=True)
