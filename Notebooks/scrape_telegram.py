import os
import json
import logging
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# Configure logging
logging.basicConfig(
    filename='scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Telegram API credentials
api_id = 27006778
api_hash = 'f41204fef3102a1ca48d248f3c287425'
phone = '+251924246518'
client = TelegramClient('session', api_id, api_hash)

# Directory to store raw data
RAW_DATA_DIR = 'data/telegram_messages/'

# Ensure the directory exists
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# List of channels to scrape
CHANNELS = [
    "lobelia4cosmetics",
    "tikvahpharma",
    "CheMed123"
    
]

async def scrape_channel(channel_username, limit=10000):
    try:
        await client.start()
        logging.info(f"Scraping messages from {channel_username}")
        
        messages = await client.get_messages(channel_username, limit=limit)
        channel_dir = os.path.join(RAW_DATA_DIR, channel_username)
        os.makedirs(channel_dir, exist_ok=True)
        
        scraped_data = []
        
        for i, message in enumerate(messages):
            message_info = {'date': message.date.isoformat()}
            if message.text:
                message_info['text'] = message.text
            
            if message.media and isinstance(message.media, MessageMediaPhoto):
                file_path = await message.download_media(file=channel_dir)
                message_info['photo'] = file_path
                logging.info(f"Saved image to: {file_path}")
            
            scraped_data.append(message_info)
            logging.info(f"Scraped message {i + 1} from {channel_username}")

        # Save raw data to JSON
        if scraped_data:
            today = datetime.now().strftime('%Y-%m-%d')
            file_path = os.path.join(channel_dir, f"{today}.json")
            with open(file_path, 'w') as f:
                json.dump(scraped_data, f, indent=4)
            logging.info(f"Saved {len(scraped_data)} messages to {file_path}")
        else:
            logging.warning(f"No messages found in {channel_username}.")

    except Exception as e:
        logging.error(f"Failed to scrape {channel_username}: {str(e)}")
    finally:
        await client.disconnect()

async def main():
    for channel in CHANNELS:
        await scrape_channel(channel)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())