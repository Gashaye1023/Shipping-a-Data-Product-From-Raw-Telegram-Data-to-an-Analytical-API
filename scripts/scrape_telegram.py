
import os
import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import configparser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config_file = 'config.ini'

if not os.path.exists(config_file):
    logger.error(f"{config_file} not found. Creating template.")
    config['Telegram'] = {
        'api_id': '27006778',
        'api_hash': 'f41204fef3102a1ca48d248f3c287425',
        'phone': '+251924246518'
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
    logger.info(f"Created {config_file} template. Fill in your credentials.")
    exit()

config.read(config_file, encoding='utf-8')

try:
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']
    phone = config['Telegram']['phone']
    
    if api_id == 'YOUR_API_ID' or api_hash == 'YOUR_API_HASH' or phone == 'YOUR_PHONE_NUMBER':
        raise ValueError("Invalid credentials.")
except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
    logger.error(str(e))
    exit()

channels = [
    'lobelia4cosmetics',
    'tikvahpharma',
    'Chemed123'
]
DATA_LAKE_PATH = 'data/raw/telegram_messages'

async def scrape_channel(client, channel_url):
    channel_name = channel_url.split('/')[-1]
    entity = await client.get_entity(channel_url)
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join(DATA_LAKE_PATH, today, channel_name)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{channel_name}_{today}.json')

    messages_data = []
    logger.info(f"Scraping channel: {channel_name}")

    async for message in client.iter_messages(entity, limit=100):
        message_data = {
            'id': message.id,
            'date': message.date.isoformat(),
            'text': message.text,
            'sender_id': message.sender_id,
            'has_media': message.media is not None,
            'media_type': 'photo' if message.media and hasattr(message.media, 'photo') else None,
            'media_path': None
        }

        if message_data['has_media']:
            media_dir = os.path.join(output_dir, 'media')
            os.makedirs(media_dir, exist_ok=True)
            media_path = os.path.join(media_dir, f'message_{message.id}.jpg')
            await client.download_media(message.media, media_path)
            message_data['media_path'] = media_path
            logger.info(f"Downloaded media for message {message.id}")

        messages_data.append(message_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Scraped {len(messages_data)} messages from {channel_name}")

async def main():
    client = TelegramClient('session_name', api_id, api_hash)

    async with client:
        await client.start(phone=phone)
        if not await client.is_user_authorized():
            try:
                await client.sign_in(phone=phone)
            except SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)

        for channel in channels:
            await scrape_channel(client, channel)

if __name__ == '__main__':
    asyncio.run(main())