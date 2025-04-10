from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.models import Group, User, Message, LastSavedMessage, Media, GroupPydantic, UserPydantic, MessagePydantic, MediaPydantic
import logging
from typing import List, Dict
import datetime

DATABASE_URL = "postgresql+asyncpg://meta:123456@localhost/baza"
engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_or_create_group(group_data: GroupPydantic, session: AsyncSession) -> Group:
    """Guruhni Pydantic bilan tekshirib, olish yoki yaratish"""
    stmt = select(Group).where(Group.id == group_data.id)
    result = await session.execute(stmt)
    group = result.scalar_one_or_none()
    
    if not group:
        group = Group(
            id=group_data.id,
            name=group_data.name,
            username=group_data.username,
            bio=group_data.bio,
            member_count=group_data.member_count,
            created_at=group_data.created_at,
            group_type=group_data.group_type,
            profile_photo=group_data.profile_photo
        )
        session.add(group)
    else:
        group.name = group_data.name
        if group_data.member_count is not None:
            group.member_count = group_data.member_count
        if group_data.bio is not None:
            group.bio = group_data.bio
        if group_data.profile_photo is not None:
            group.profile_photo = group_data.profile_photo
    return group

async def get_or_create_user(user_data: UserPydantic, session: AsyncSession) -> User:
    """Foydalanuvchini Pydantic bilan tekshirib, olish yoki yaratish"""
    stmt = select(User).where(User.id == user_data.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=user_data.id,
            first_name=user_data.first_name,
            username=user_data.username,
            profile_photo=user_data.profile_photo,
            last_seen=user_data.last_seen,
            is_bot=user_data.is_bot,
            phone_number=user_data.phone_number
        )
        session.add(user)
    else:
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.profile_photo is not None:
            user.profile_photo = user_data.profile_photo
    return user

async def get_last_saved_message(group_id: int, session: AsyncSession) -> LastSavedMessage:
    stmt = select(LastSavedMessage).where(LastSavedMessage.group_id == group_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def update_last_saved_message(group_id: int, message_id: int, timestamp: datetime.datetime, session: AsyncSession):
    last_saved = await get_last_saved_message(group_id, session)
    if last_saved:
        last_saved.last_message_id = message_id
        last_saved.last_timestamp = timestamp
    else:
        last_saved = LastSavedMessage(
            group_id=group_id,
            last_message_id=message_id,
            last_timestamp=timestamp
        )
        session.add(last_saved)

async def save_messages(messages: List[dict], logger: logging.Logger) -> None:
    async with async_session() as session:
        try:
            for msg in messages:
                db_msg = Message(**msg)
                session.add(db_msg)
            await session.commit()
            logger.info(f"{len(messages)} ta xabar databazaga saqlandi")
        except Exception as e:
            await session.rollback()
            logger.error(f"Xabarlarni saqlashda xato: {e}")





# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from config import DB_CONFIG
# from src.models import Base, Message
# import logging

# engine = create_async_engine(
#     f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}",
#     echo=True
# )
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# async def init_db():
#     """Jadvalni yaratish"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)  # Eski jadvalni o‘chirish
#         await conn.run_sync(Base.metadata.create_all)  # Yangisini yaratish

# async def save_messages(message_buffer, logger):
    # """Xabarlarni saqlash"""
    # async with async_session() as session:
    #     try:
    #         for data in message_buffer:
    #             exists = await session.get(Message, data["id"])
    #             if exists:
    #                 logger.info(f"Xabar ID {data['id']} allaqachon mavjud")
    #                 continue
    #             message = Message(
    #                 id=data["id"],
    #                 group_id=data["group_id"],
    #                 account_name=data["account_name"],
    #                 text=data["text"],
    #                 timestamp=data["timestamp"],
    #                 url=data["url"],
    #                 user_id=data["user_id"],
    #                 user_first_name=data["user_first_name"],
    #                 user_username=data["user_username"],
    #                 user_profile_photo=data.get("user_profile_photo"),  # Keyinchalik
    #                 group_profile_photo=data.get("group_profile_photo")  # Keyinchalik
    #             )
    #             session.add(message)
    #         await session.commit()
    #         logger.info(f"{len(message_buffer)} ta xabar saqlandi")
    #         message_buffer.clear()
    #     except Exception as e:
    #         await session.rollback()
    #         logger.error(f"DB xatosi: {str(e)}")