from ..clients.telegram import get_client

bot_token = "1207410875:AAFvIwYtKpIkkf1_TfbLyRs2CUpiPN_pG10"


async def send_message_to_channel(channel: int):
    # Start the client
    client = await get_client()
    await client.send_message(channel, "Hello!")
