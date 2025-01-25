import uvicorn
import os
from fastapi import FastAPI
from senpy_ai_chatbot.features.send_channel_message import send_message_to_channel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})


@app.get("/news-report")
def get_news_report():
    return {"report": "yo"}


@app.get("/send-message")
async def send_test_message():
    await send_message_to_channel(int(os.getenv("TELEGRAM_CHANNEL_ID") or -1))


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run("senpy_ai_chatbot.main:app", host="0.0.0.0", port=8000, reload=True)
