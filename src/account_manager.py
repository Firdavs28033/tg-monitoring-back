from pyrogram import Client
from config import ACCOUNTS, SESSION_DIR, ACCOUNTS_DIR
import os

class AccountManager:
    def __init__(self):
        self.clients = {}

    def load_accounts(self, logger):
        for idx, account in enumerate(ACCOUNTS, 1):
            account_name = f"account{idx}"
            if not all([account["api_id"], account["api_hash"], account["phone"]]):
                logger.error(f"{account_name} uchun to‘liq ma'lumot yo‘q")
                continue
            client = Client(
                account_name,
                api_id=account["api_id"],
                api_hash=account["api_hash"],
                phone_number=account["phone"],
                password=account["password"],
                workdir=SESSION_DIR
            )
            client.name = account_name  # Handler uchun qo‘shildi
            group_file = os.path.join(ACCOUNTS_DIR, f"{account_name}.txt")
            groups = []
            if os.path.exists(group_file):
                with open(group_file, "r") as f:
                    groups = [line.strip() for line in f if line.strip()]
            else:
                logger.warning(f"{account_name} uchun guruhlar fayli topilmadi")
            self.clients[account_name] = {"client": client, "groups": groups}
            logger.info(f"{account_name} yuklandi: {len(groups)} ta guruh")

    async def start_clients(self):
        for account_name, info in self.clients.items():
            await info["client"].start()

    async def stop_clients(self):
        for account_name, info in self.clients.items():
            await info["client"].stop()

    def get_clients(self):
        return self.clients