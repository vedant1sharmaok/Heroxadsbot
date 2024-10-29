import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsSearch
from flask import Flask, jsonify, request

# Replace these with your own values
API_ID = '23957241'
API_HASH = 'c806d41322a1d13b32e910b39c138fc8'
STRING_SESSION = '1BVtsOJgBu46oxM2FjD64dZxr3zQWbloyopB-jRND5tOhzr21Ov1ghZgEw1JVfdwEapswKVC0m7dfj9YcC2R2CUK6zaV-STGdmA_cdQ6aHVzZf530n94xhcD6lE5xCFmtxyrdNQoD-4i71rMHW1alJiLEJQMujlku4CBb-7Lhu0QFugT9h_9K1DAglQWjBjMKw1_BM6KizWkJMprmC8LPZxxFycPzM1p1xIrve_EUJVclIWEal-RRoEVQhTMpmnfzZGBS7_Dynv7qMNIQpC36ZiFIid0z_oce9pesuR3zlCaiaeKLZhQN6-REg_Dj6gqlE2JuRjQWcMJJhmQvx8YvkebV43ZoaXo='
CHANNEL_USERNAME = 'YOUR_CHANNEL_USERNAME'  # Channel from which to forward messages

app = Flask(__name__)

client = TelegramClient('session_name', API_ID, API_HASH).start(session=STRING_SESSION)

# Global variable to control forwarding status and interval
forwarding = False
interval = 60  # Default interval in seconds

async def get_joined_groups():
    """Fetch all groups the bot is a member of."""
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            groups.append(dialog.entity)
    return groups

async def forward_message():
    global forwarding
    async with client:
        while forwarding:
            async for message in client.iter_messages(CHANNEL_USERNAME, limit=1):
                if forwarding:
                    groups = await get_joined_groups()
                    for group in groups:
                        await client.send_message(group, message)  # Forward message to each group
            await asyncio.sleep(interval)

@app.route('/start', methods=['GET'])
def start_forwarding():
    global forwarding
    if not forwarding:
        forwarding = True
        loop.create_task(forward_message())
        return jsonify({"status": "Forwarding started"})
    else:
        return jsonify({"status": "Already forwarding"})

@app.route('/stop', methods=['GET'])
def stop_forwarding():
    global forwarding
    forwarding = False
    return jsonify({"status": "Forwarding stopped"})

@app.route('/set_interval', methods=['POST'])
def set_interval():
    global interval
    data = request.json
    if 'interval' in data:
        interval = data['interval'] * 60  # Convert minutes to seconds
        return jsonify({"status": "Interval updated", "interval": interval // 60})
    return jsonify({"status": "Invalid input"}), 400

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start())
    app.run(port=5000)
