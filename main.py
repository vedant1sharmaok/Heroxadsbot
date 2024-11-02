from telethon import TelegramClient, events
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your API credentials and bot token
API_ID = 'YOUR_API_ID'  # Your API ID from my.telegram.org
API_HASH = 'YOUR_API_HASH'  # Your API Hash from my.telegram.org
BOT_TOKEN = 'YOUR_BOT_TOKEN'  # Your Bot Token from BotFather
PHONE = 'YOUR_PHONE_NUMBER'  # Your phone number for user authentication

# Create a client instance for the user account
client = TelegramClient('user_session', API_ID, API_HASH)

# Create a client instance for the bot
bot_client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def main():
    await client.start()
    await bot_client.start()
    logger.info("Bot is running...")

    # Get all dialogs (channels and groups)
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            groups.append(dialog)
            logger.info(f"Joined Group: {dialog.name} (ID: {dialog.id})")

    # Specify the channel to forward messages from
    channel = 'YOUR_CHANNEL_USERNAME'  # Replace with your channel username or ID

    while True:
        try:
            # Get the last message from the channel
            async for message in client.iter_messages(channel, limit=1):
                logger.info(f"New message from {channel}: {message.text}")

                # Forward the message to all groups
                for group in groups:
                    try:
                        await bot_client.forward_messages(group.id, message)
                        logger.info(f"Forwarded message to group: {group.name}")
                    except Exception as e:
                        logger.error(f"Error forwarding to {group.name}: {e}")

            # Wait for a custom interval before checking again (in seconds)
            await asyncio.sleep(60)  # Change this to your desired interval

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(10)  # Wait before retrying

# Run the main function
with client:
    client.loop.run_until_complete(main())
