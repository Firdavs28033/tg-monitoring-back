import sys
import os
from typing import List, Dict, Optional, Any
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message as PyrogramMessage
from pyrogram.errors import PeerIdInvalid, InviteHashExpired, UserAlreadyParticipant
from src.account_manager import AccountManager
from src.database import save_messages
from src.analytics import MessageAnalytics
from src.models import MessagePydantic, GroupPydantic, UserPydantic
from logger import setup_logger
import logging
from pydantic import ValidationError

async def is_valid_message(text: Optional[str]) -> bool:
    """Xabar validligini tekshiradi."""
    if not text or text.strip() == "" or text == "Bo‘sh xabar":
        return False
    words = text.split()
    return not (len(words) == 1 and len(words[0]) <= 2) and len(words) <= 500

async def on_message_handler(client: Client, message: PyrogramMessage) -> None:
    """Yangi xabarlar uchun handler."""
    logger = setup_logger()
    text = message.text or "Bo‘sh xabar"
    
    if not await is_valid_message(text):
        logger.info(f"Xabar ID {message.id} validatsiyadan o‘tmadi: {text[:50]}...")
        return
    
    try:
        group_data = {
            "id": message.chat.id,
            "name": message.chat.title or "Noma'lum guruh",
            "username": message.chat.username,
            "bio": message.chat.description,
            "member_count": message.chat.members_count,
            "created_at": None,
            "profile_photo": None
        }
        GroupPydantic(**group_data)

        user_data = None
        if message.from_user:
            user_data = {
                "id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "username": message.from_user.username,
                "profile_photo": None,
                "last_seen": message.from_user.last_seen if hasattr(message.from_user, "last_seen") else None,
                "is_bot": message.from_user.is_bot
            }
            UserPydantic(**user_data)

        url = f"https://t.me/c/{str(message.chat.id)[4:]}/{message.id}"
        message_data = {
            "id": message.id,
            "group_id": message.chat.id,
            "user_id": message.from_user.id if message.from_user else None,
            "account_name": client.name,
            "text": text,
            "timestamp": message.date.isoformat(),
            "url": url,
            "group_name": group_data["name"],
            "group_username": group_data["username"],
            "group_bio": group_data["bio"],
            "group_member_count": group_data["member_count"],
            "user_first_name": user_data["first_name"] if user_data else None,
            "user_username": user_data["username"] if user_data else None,
            "user_profile_photo": None,
            "media": []
        }

        if message.photo:
            file_path = await client.download_media(message.photo, file_name=f"static/media/photos/{message.id}.jpg")
            message_data["media"].append({
                "file_type": "photo",
                "file_path": file_path,
                "file_size": message.photo.file_size
            })

        MessagePydantic(**message_data)
        await save_messages([message_data], logger)
        analytics = MessageAnalytics()
        analytics.analyze_message(message_data["text"])
        logger.info(f"Yangi xabar ID: {message_data['id']}, Guruh: {message_data['group_id']}, Matn: {message_data['text'][:50]}...")
        print(f"[{client.name}] Yangi xabar: Guruh ID: {message.chat.id}, Xabar ID: {message.id}, Matn: {text[:50]}", flush=True)
        analytics.print_stats()

    except ValidationError as e:
        logger.error(f"Xabar ID {message.id} validatsiyadan o‘tmadi: {e}")
    except Exception as e:
        logger.error(f"Xabar ID {message.id} ni qayta ishlashda xato: {e}")

async def resolve_chat_ids(client: Client, groups: List[Dict[str, str]], logger: logging.Logger) -> List[int]:
    """@username, ID yoki invite link’larni chat_id’larga aylantiradi."""
    chat_ids = []
    for group in groups:
        group_identifier = group.get("username") or group.get("id")
        invite_link = group.get("invite_link")
        
        try:
            # Guruh ID bo‘lsa
            if group_identifier and (isinstance(group_identifier, int) or str(group_identifier).startswith("-100")):
                chat_id = int(group_identifier)
                chat = await client.get_chat(chat_id)
                logger.info(f"Guruh ID {chat_id} tasdiqlandi: {chat.title}")
                chat_ids.append(chat_id)
            # @username bo‘lsa
            elif group_identifier and isinstance(group_identifier, str) and group_identifier.startswith("@"):
                chat = await client.get_chat(group_identifier)
                chat_id = chat.id
                logger.info(f"{group_identifier} -> Chat ID: {chat_id}")
                chat_ids.append(chat_id)
            # Invite link bo‘lsa
            elif invite_link:
                try:
                    chat = await client.join_chat(invite_link)
                    chat_id = chat.id
                    logger.info(f"{invite_link} orqali guruhga qo‘shildi -> Chat ID: {chat_id}")
                    chat_ids.append(chat_id)
                except UserAlreadyParticipant:
                    # Foydalanuvchi guruhda bo‘lsa, chat_id’ni aniqlash uchun guruh tarixidan foydalanamiz
                    async for msg in client.get_chat_history(chat_id=None, limit=1):
                        if msg.chat and msg.chat.type in ["group", "supergroup"]:
                            chat_id = msg.chat.id
                            logger.info(f"{invite_link} allaqachon qo‘shilgan -> Chat ID: {chat_id}")
                            chat_ids.append(chat_id)
                            break
                    else:
                        logger.error(f"{invite_link} dan chat ID’ni aniqlab bo‘lmadi. To‘g‘ri chat ID’ni qo‘lda kiriting!")
            else:
                logger.warning(f"{group} noto‘g‘ri formatda: @username, -100 bilan boshlanadigan ID yoki invite_link kutilmoqda")
        
        except PeerIdInvalid:
            logger.error(f"{group_identifier or invite_link} ni chat_id ga aylantirishda xato: PEER_ID_INVALID. Guruhga qo‘shiling!")
        except InviteHashExpired:
            logger.error(f"{invite_link} taklif havolasi eskirgan!")
        except ValueError:
            logger.error(f"{group_identifier} ni int ga aylantirib bo‘lmadi: Noto‘g‘ri ID formati")
        except Exception as e:
            logger.error(f"{group_identifier or invite_link} ni chat_id ga aylantirishda xato: {e}")
            await asyncio.sleep(1)
    
    return chat_ids

async def collect_history(client: Client, chat_id: int, logger: logging.Logger, buffer_size: int = 100) -> None:
    """Guruhdagi eski xabarlarni yig‘adi va saqlaydi."""
    message_buffer = []
    
    try:
        async for message in client.get_chat_history(chat_id, limit=0):
            text = message.text or "Bo‘sh xabar"
            if not await is_valid_message(text):
                continue
            
            url = f"https://t.me/c/{str(message.chat.id)[4:]}/{message.id}"
            user_data = {
                "id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "username": message.from_user.username,
                "profile_photo": None
            } if message.from_user else {}
            
            message_data = {
                "id": message.id,
                "group_id": chat_id,
                "user_id": user_data.get("id"),
                "account_name": client.name,
                "text": text,
                "timestamp": message.date.isoformat(),
                "url": url,
                "group_name": message.chat.title or "Noma'lum guruh",
                "group_username": message.chat.username,
                "group_bio": message.chat.description,
                "group_member_count": message.chat.members_count,
                "user_first_name": user_data.get("first_name"),
                "user_username": user_data.get("username"),
                "user_profile_photo": None,
                "media": []
            }
            
            try:
                MessagePydantic(**message_data)
                message_buffer.append(message_data)
                
                if len(message_buffer) >= buffer_size:
                    await save_messages(message_buffer, logger)
                    logger.info(f"{buffer_size} ta eski xabar saqlandi")
                    message_buffer.clear()
            except ValidationError as e:
                logger.error(f"Eski xabar ID {message.id} validatsiyadan o‘tmadi: {e}")
        
        if message_buffer:
            await save_messages(message_buffer, logger)
            logger.info(f"{len(message_buffer)} ta qolgan eski xabar saqlandi")
    
    except Exception as e:
        logger.error(f"{chat_id} guruhidan tarixni yig‘ishda xato: {e}")

async def setup_client(client: Client, groups: List[Dict[str, str]], logger: logging.Logger) -> None:
    """Klientni sozlash va handler’larni qo‘shish."""
    await client.start()
    chat_ids = await resolve_chat_ids(client, groups, logger)
    logger.info(f"{client.name} uchun chat ID’lari: {chat_ids}")
    
    for chat_id in chat_ids:
        logger.info(f"{chat_id} guruhidan eski xabarlar yig‘ilmoqda...")
        await collect_history(client, chat_id, logger)
    
    if chat_ids:
        async def wrapped_handler(client: Client, message: PyrogramMessage):
            await on_message_handler(client, message)
        
        handler = MessageHandler(wrapped_handler, filters.chat(chat_ids))
        client.add_handler(handler)
    else:
        logger.warning(f"{client.name} uchun hech qanday chat ID topilmadi")

async def main() -> None:
    """Asosiy dastur logikasi."""
    logger = setup_logger()
    logger.info("Real-time xabar yig‘ish boshlandi...")
    
    account_manager = AccountManager()
    account_manager.load_accounts(logger)
    clients = account_manager.get_clients()
    
    if not clients:
        logger.error("Hech qanday hisob yuklanmadi!")
        return
    
    tasks = []
    for account_name, info in clients.items():
        client: Client = info["client"]
        groups: List[Dict[str, str]] = [
            {"username": g} if isinstance(g, str) and g.startswith("@") 
            else {"id": g} if isinstance(g, (str, int)) and str(g).startswith("-100")
            else {"invite_link": g} if isinstance(g, str) and g.startswith("https://t.me/")
            else {"username": str(g)} for g in info["groups"]
        ]
        logger.info(f"{account_name} uchun guruhlar: {groups}")
        tasks.append(setup_client(client, groups, logger))
    
    await asyncio.gather(*tasks)
    logger.info("Barcha hisoblar ishga tushdi va xabarlar kutilmoqda...")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())