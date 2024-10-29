import asyncio
from telethon import TelegramClient
from flask import Flask, jsonify
import time

# Replace these with your own values
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
STRING_SESSION = 'YOUR_STRING_SESSION'
CHANNEL_USERNAME = 'YOUR_CHANNEL_USERNAME'  # Channel from which to forward messages
GROUPS = ['group1_username', 'group2_username']  # List of groups to forward messages to

app = Flask(__name__)

client = TelegramClient('session_name', API_ID, API_HASH).start(session=STRING_SESSION)

async def forward_message():
    async with client:
        while True:
            async for message in client.iter_messages(CHANNEL_USERNAME, limit=1):
                for group in GROUPS:
                    await client.send_message(group, message)
            await asyncio.sleep(60)  # Time interval in seconds

@app.route('/start', methods=['GET'])
def start_forwarding():
    loop.create_task(forward_message())
    return jsonify({"status": "Forwarding started"})

@app.route('/stop', methods=['GET'])
def stop_forwarding():
    # Implement logic to stop forwarding if needed
    return jsonify({"status": "Forwarding stopped"})

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start())
    app.run(port=5000)
