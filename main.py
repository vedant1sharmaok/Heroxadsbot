import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telethon import TelegramClient, errors
from telethon.tl.types import PeerChannel

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your own values
API_ID = '23957241'
API_HASH = 'c806d41322a1d13b32e910b39c138fc8'
BOT_TOKEN = '8153725483:AAHZorPFnW4iUojWIFBPKDnNNagIz5mGAnU'

# Initialize Telethon client
client = TelegramClient('session_name', API_ID, API_HASH)

# Store channels for forwarding messages
forwarding_channels = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your forwarding bot. Use /add_channel <username> to add a channel.')

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        username = context.args[0].strip('@')
        try:
            # Check if the username is valid and get the channel entity
            channel = await client.get_entity(username)
            if isinstance(channel, PeerChannel):
                forwarding_channels[username] = channel
                await update.message.reply_text(f'Channel @{username} added successfully!')
            else:
                await update.message.reply_text('The provided username is not a channel.')
        except errors.UsernameNotOccupiedError:
            await update.message.reply_text('The provided username does not exist.')
        except Exception as e:
            logger.error(f'Error adding channel: {e}')
            await update.message.reply_text('An error occurred while adding the channel.')
    else:
        await update.message.reply_text('Please provide a channel username.')

async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not forwarding_channels:
        await update.message.reply_text('No channels have been added for forwarding messages.')
        return

    message = ' '.join(context.args) if context.args else 'Forwarded message from bot.'
    formatted_message = f"*Forwarded Message:* {message}"

    async with client:
        for username, channel in forwarding_channels.items():
            try:
                await client.send_message(channel, formatted_message)
                logger.info(f'Message forwarded to @{username}')
            except Exception as e:
                logger.error(f'Error forwarding message to @{username}: {e}')

    await update.message.reply_text('Message forwarded to all added channels.')

async def main() -> None:
    # Start the bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_channel", add_channel))
    application.add_handler(CommandHandler("forward", forward_messages))

    # Start polling
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
