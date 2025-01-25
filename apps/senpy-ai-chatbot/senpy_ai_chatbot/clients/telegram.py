from telethon import TelegramClient
from telethon.sessions import MemorySession
from telethon.tl.functions.channels import JoinChannelRequest


# TODO: get real data Initialize the Telegram bot
api_id = 788409
api_hash = "a2ccfb84acc66bc5160a9ffd4ab76fa0"
bot_token = "1207410875:AAFvIwYtKpIkkf1_TfbLyRs2CUpiPN_pG10"


async def get_client():
    # TODO: think if I need a once-per-application-lifetime session and nbot everytime created session when I turn to client
    client = TelegramClient(MemorySession(), api_id, api_hash)
    await client.connect()

    await client.sign_in(bot_token=bot_token)
    return client
