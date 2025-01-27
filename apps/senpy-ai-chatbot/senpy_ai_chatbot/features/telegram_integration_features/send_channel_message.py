import os

from dotenv import load_dotenv
from .telegram_client import get_client

load_dotenv()


async def send_message_to_channel(message: str, telegram_channel_id: int | None):
    # Start the client
    channel = telegram_channel_id or int(os.getenv("TELEGRAM_CHANNEL_ID") or "-1")

    if not channel or not message:
        raise Exception("Channel and message are required")

    client = await get_client()
    await client.send_message(channel, message)
