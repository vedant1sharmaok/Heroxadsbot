from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telethon import TelegramClient
import json
import os

app = Flask(__name__)

# Store accounts in a dictionary
accounts = {}
AUTHORIZED_USERS = set()  # Set of authorized user IDs

# Load accounts from a JSON file
def load_accounts():
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f:
            return json.load(f)
    return {}

# Save accounts to a JSON file
def save_accounts():
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f)

# Initialize Telethon clients for each account
def init_client(api_id, api_hash, phone):
    return TelegramClient(phone, api_id, api_hash)

# Command to start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Use /authorize to gain access.")

# Command to authorize user
def authorize(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    AUTHORIZED_USERS.add(user_id)
    update.message.reply_text("You have been authorized! You can now use commands.")

# Command to list accounts
def list_accounts(update: Update, context: CallbackContext):
    if not is_authorized(update):
        return

    if accounts:
        account_list = "n".join(accounts.keys())
        update.message.reply_text(f"Accounts:n{account_list}")
    else:
        update.message.reply_text("No accounts have been added yet.")

# Command to add an account
def add_account(update: Update, context: CallbackContext):
    if not is_authorized(update):
        return

    if len(context.args) < 3:
        update.message.reply_text("Usage: /add_account <api_id> <api_hash> <phone_number>")
        return

    api_id = context.args[0]
    api_hash = context.args[1]
    phone_number = context.args[2]

    # Initialize and store the client
    try:
        client = init_client(api_id, api_hash, phone_number)
        accounts[phone_number] = {'api_id': api_id, 'api_hash': api_hash}
        save_accounts()  # Save changes persistently
        update.message.reply_text(f"Account {phone_number} added successfully!")
    except Exception as e:
        update.message.reply_text(f"Error adding account: {str(e)}")

# Command to remove an account
def remove_account(update: Update, context: CallbackContext):
    if not is_authorized(update):
        return

    if len(context.args) < 1:
        update.message.reply_text("Usage: /remove_account <phone_number>")
        return

    phone_number = context.args[0]
    if phone_number in accounts:
        del accounts[phone_number]
        save_accounts()  # Save changes persistently
        update.message.reply_text(f"Account {phone_number} removed successfully!")
    else:
        update.message.reply_text(f"No account found for {phone_number}.")

# Command to forward messages
def forward(update: Update, context: CallbackContext):
    if not is_authorized(update):
        return
            if len(context.args) < 3:
        update.message.reply_text("Usage: /forward <from_chat_id> <to_chat_id> <phone_number>")
        return

    from_chat_id = context.args[0]
    to_chat_id = context.args[1]
    phone_number = context.args[2]

    if phone_number not in accounts:
        update.message.reply_text(f"No account found for {phone_number}.")
        return

    client = init_client(accounts[phone_number]['api_id'], accounts[phone_number]['api_hash'], phone_number)

    async def forward_message():
        await client.start()
        async for message in client.iter_messages(from_chat_id):
            await client.send_message(to_chat_id, message.text)
            update.message.reply_text(f"Forwarded message from {from_chat_id} to {to_chat_id}")

    with client:
        client.loop.run_until_complete(forward_message())

# Check if user is authorized
def is_authorized(update: Update) -> bool:
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("You are not authorized to use this command. Please use /authorize.")
        return False
    return True

# Set up the Telegram bot
def main():
    global accounts
    accounts = load_accounts()  # Load existing accounts at startup

    updater = Updater("YOUR_BOT_TOKEN")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("authorize", authorize))
    dp.add_handler(CommandHandler("list_accounts", list_accounts))
    dp.add_handler(CommandHandler("add_account", add_account))
    dp.add_handler(CommandHandler("remove_account", remove_account))
    dp.add_handler(CommandHandler("forward", forward))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
