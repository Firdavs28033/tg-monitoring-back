
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNTS = [
    {"api_id": os.getenv("API_ID_1"), "api_hash": os.getenv("API_HASH_1"), "phone": os.getenv("PHONE_1"), "password": os.getenv("PASSWORD_1")},
    {"api_id": os.getenv("API_ID_2"), "api_hash": os.getenv("API_HASH_2"), "phone": os.getenv("PHONE_2"), "password": os.getenv("PASSWORD_2")},
]

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST", "localhost")
}

ACCOUNTS_DIR = os.path.join(os.path.dirname(__file__), "accounts")
SESSION_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(ACCOUNTS_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)