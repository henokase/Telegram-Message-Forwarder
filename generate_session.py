from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\nHere is your session string, please save it safely:\n")
    print(client.session.save())
    print("\nAdd this string to your environment variables as TELEGRAM_SESSION_STRING") 