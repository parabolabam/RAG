from ..clients.telegram import get_client


async def send_message_to_channel(channel: int, message: str):
    # Start the client
    if not channel or not message:
        raise Exception("Channel and message are required")

    client = await get_client()
    await client.send_message(channel, message)
