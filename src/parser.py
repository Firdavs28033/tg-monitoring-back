from typing import Dict, List, Any
from pyrogram import Client
from src.models import MessagePydantic, GroupPydantic, UserPydantic
import logging
import asyncio
from pydantic import ValidationError
async def fetch_messages(clients: Dict[str, Dict[str, Any]], message_buffer: List[Dict], logger: logging.Logger, batch_size: int = 100) -> None:
    from src.database import save_messages
    for account_name, info in clients.items():
        client: Client = info["client"]
        groups: List[str] = info["groups"]
        
        for group in groups:
            logger.info(f"{account_name} uchun {group} guruhidan xabarlar yig‘ilmoqda...")
            try:
                chat = await client.get_chat(group)
                group_data = {
                    "id": chat.id,
                    "name": chat.title or "Noma'lum guruh",
                    "username": chat.username,
                    "bio": chat.description,
                    "member_count": chat.members_count,
                    "created_at": chat.date,
                    "profile_photo": None
                }
                GroupPydantic(**group_data)

                async for message in client.get_chat_history(chat.id, limit=batch_size):
                    try:
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

                        message_data = {
                            "id": message.id,
                            "group_id": chat.id,
                            "user_id": message.from_user.id if message.from_user else None,
                            "account_name": account_name,
                            "text": message.text or "Bo‘sh xabar",
                            "timestamp": message.date,
                            "url": f"https://t.me/c/{str(chat.id)[4:]}/{message.id}",
                            "group_name": group_data["name"],
                            "group_username": group_data["username"],
                            "group_bio": group_data["bio"],
                            "group_member_count": group_data["member_count"],
                            "user_first_name": user_data["first_name"] if user_data else None,
                            "user_username": user_data["username"] if user_data else None,
                            "user_profile_photo": user_data["profile_photo"] if user_data else None,
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
                        message_buffer.append(message_data)
                        logger.info(f"Xabar ID: {message_data['id']}, Matn: {message_data['text'][:50]}... saqlandi")

                        if len(message_buffer) >= batch_size:
                            await save_messages(message_buffer, logger)
                            message_buffer.clear()

                    except ValidationError as e:
                        logger.error(f"Xabar ID {message.id} validatsiyadan o‘tmadi: {e}")
                    except Exception as e:
                        logger.error(f"Xabar ID {message.id} ni qayta ishlashda xato: {e}")

                await asyncio.sleep(0.5)  # API limitlaridan qochish

            except Exception as e:
                logger.error(f"{group} guruhida umumiy xato: {e}")
                await asyncio.sleep(1)






















# async def fetch_messages(clients, message_buffer, logger):
#     """Har bir hisobdan guruhlar bo‘yicha xabar yig‘ish"""
#     for account_name, info in clients.items():
#         client = info["client"]
#         groups = info["groups"]
#         for group in groups:
#             logger.info(f"{account_name} uchun {group} guruhidan xabarlar yig‘ilmoqda...")
#             try:
#                 async for message in client.get_chat_history(group, limit=5):  # Sinov uchun 5 ta xabar
#                     data = {
#                         "id": message.id,
#                         "group_id": message.chat.id,
#                         "account_name": account_name,
#                         "text": message.text or "Bo‘sh xabar",
#                         "timestamp": message.date
#                     }
#                     message_buffer.append(data)
#                     logger.info(f"Xabar ID: {data['id']}, Matn: {data['text'][:50]}...")
#             except Exception as e:
#                 logger.error(f"{group} guruhida xato: {e}")