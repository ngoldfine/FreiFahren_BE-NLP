from telethon import TelegramClient
from datetime import datetime, timedelta, timezone
import asyncio
from dotenv import load_dotenv
import csv
import os

load_dotenv()

# Your credentials from my.telegram.org
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# The name of the session file.
session_file = 'Get1000Messages'

# Target group username or group ID
group_identifier = '@freifahren_BE'

client = TelegramClient(session_file, api_id, api_hash)


async def get_messages(group_identifier):
    await client.start()
    print('Client Created')

    # The timeframe for messages to fetch, making them timezone aware
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)

    message_texts = []

    # Fetch a large number of messages first, to filter through
    all_messages = await client.get_messages(group_identifier, limit=5000)
    
    for message in all_messages:
        if start_time <= message.date <= end_time:
            # Append both message text and the timestamp
            message_texts.append((message.message, message.date.strftime('%Y-%m-%d %H:%M:%S')))
        # Break early if message is older than our timeframe
        if message.date < start_time:
            break

    await client.disconnect()
    return message_texts

if __name__ == '__main__':
    messages = asyncio.run(get_messages(group_identifier))

    # Save the messages to a CSV file
    with open('group_messages.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for message_text, timestamp in messages:
            # Write each message text and its timestamp as a row in the CSV file
            writer.writerow([message_text, timestamp])
