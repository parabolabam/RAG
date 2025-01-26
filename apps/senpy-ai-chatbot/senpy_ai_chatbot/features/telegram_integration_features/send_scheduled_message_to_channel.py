import os

from dotenv import load_dotenv
from openai.types.chat import ChatCompletionMessage
from telethon.hints import DateLike
from .telegram_client import get_client

load_dotenv()


async def send_scheduled_message_to_channel(
    message: ChatCompletionMessage, when: DateLike
):
    channel = int(os.getenv("TELEGRAM_CHANNEL_ID") or "-1")

    if not channel or not message:
        raise Exception("Channel and message are required")

    client = await get_client()
    await client.send_message(channel, str(message), schedule=when)
