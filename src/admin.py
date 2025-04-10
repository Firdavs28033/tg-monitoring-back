import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))



from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Message  # Model faylingizdan import
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from src.models import Base, Message  # Model faylingizdan import

# FastAPI ilovasini yaratish
app = FastAPI()

# Databaza ulanishi
DATABASE_URL = "postgresql+asyncpg://meta:123456@localhost/baza"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# SQLAdmin sozlamasi
admin = Admin(app, engine)

# Message model uchun Admin view
class MessageAdmin(ModelView, model=Message):
    column_list = [Message.id, Message.group_id, Message.text, Message.timestamp, Message.url]
    column_searchable_list = [Message.text]

# Admin view’ni qo‘shish
admin.add_view(MessageAdmin)

# /messages endpoint
@app.get("/messages")
async def get_messages():
    async with async_session() as session:
        result = await session.execute(select(Message))
        messages = result.scalars().all()
        return [{"id": msg.id, "group_id": msg.group_id, "text": msg.text} for msg in messages]

# Ilovani ishga tushirish uchun: uvicorn src.admin:app --reload