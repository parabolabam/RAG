import os
from telethon import TelegramClient
from telethon.sessions import MemorySession
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")


async def get_client():
    if not api_hash or not api_id or not bot_token:
        raise Exception(
            "TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_BOT_TOKEN must be set in the environment"
        )

    # TODO: think if I need a once-per-application-lifetime session and nbot everytime created session when I turn to client
    client = TelegramClient(MemorySession(), int(api_id), api_hash)
    await client.connect()

    await client.sign_in(bot_token=bot_token)
    return client
