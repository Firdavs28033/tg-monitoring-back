from sqlalchemy import BigInteger, Column, String, DateTime, ForeignKey, Integer, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List
import datetime
import enum
import sqlalchemy

Base = declarative_base()

# Enum’lar
class GroupType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SUPERGROUP = "supergroup"

class FileType(enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    VOICE = "voice"

# SQLAlchemy modellar
class Group(Base):
    __tablename__ = "groups"
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    bio = Column(Text)
    member_count = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    group_type = Column(Enum(GroupType), default=GroupType.SUPERGROUP)
    profile_photo = Column(String)
    is_active = Column(Boolean, default=True)

    messages = relationship("Message", back_populates="group")
    last_saved = relationship("LastSavedMessage", uselist=False, back_populates="group")

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    username = Column(String, index=True)
    profile_photo = Column(String)
    last_seen = Column(DateTime(timezone=True))
    is_bot = Column(Boolean, default=False)
    phone_number = Column(String, unique=True)

    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    account_name = Column(String)
    text = Column(Text)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    url = Column(String)

    group = relationship("Group", back_populates="messages")
    user = relationship("User", back_populates="messages")
    media = relationship("Media", back_populates="message")

    __table_args__ = (
        sqlalchemy.UniqueConstraint("id", "group_id", name="uq_message_id_group_id"),
        sqlalchemy.Index("idx_group_timestamp", "group_id", "timestamp"),
    )

class LastSavedMessage(Base):
    __tablename__ = "last_saved_messages"
    group_id = Column(BigInteger, ForeignKey("groups.id"), primary_key=True)
    last_message_id = Column(BigInteger, ForeignKey("messages.id"), nullable=False)
    last_timestamp = Column(DateTime(timezone=True), nullable=False)

    group = relationship("Group", back_populates="last_saved")

class Media(Base):
    __tablename__ = "media"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey("messages.id"), nullable=False, index=True)
    file_type = Column(Enum(FileType), nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    message = relationship("Message", back_populates="media")

# Pydantic modellar
# class MediaPydantic(BaseModel):
#     file_type: FileType
#     file_path: str = Field(..., min_length=1)
#     file_size: Optional[int] = Field(None, ge=0)  # Fayl hajmi 0 yoki undan katta

#     @validator("file_path")
#     def validate_file_path(cls, v):
#         if not v.strip():
#             raise ValueError("Fayl yo‘li bo‘sh bo‘lmasligi kerak")
#         return v

# class UserPydantic(BaseModel):
#     id: int = Field(..., gt=0)  # Foydalanuvchi ID’si musbat bo‘lishi kerak
#     first_name: Optional[str] = None
#     username: Optional[str] = None
#     profile_photo: Optional[str] = None
#     last_seen: Optional[datetime.datetime] = None
#     is_bot: Optional[bool] = False
#     phone_number: Optional[str] = None

# class GroupPydantic(BaseModel):
#     id: int = Field(..., gt=0)  # Guruh ID’si musbat bo‘lishi kerak
#     name: str = Field(..., min_length=1)
#     username: Optional[str] = None
#     bio: Optional[str] = None
#     member_count: Optional[int] = Field(None, ge=0)
#     created_at: Optional[datetime.datetime] = None
#     group_type: Optional[GroupType] = GroupType.SUPERGROUP
#     profile_photo: Optional[str] = None

#     @validator("username")
#     def validate_username(cls, v):
#         if v and not v.startswith("@"):
#             raise ValueError("Username '@' bilan boshlanishi kerak")
#         return v

# class MessagePydantic(BaseModel):
#     id: int = Field(..., gt=0)  # Xabar ID’si musbat bo‘lishi kerak
#     group_id: int = Field(..., gt=0)
#     user_id: Optional[int] = Field(None, gt=0)
#     account_name: str = Field(..., min_length=1)
#     text: Optional[str] = None
#     timestamp: datetime.datetime = Field(...)
#     url: str = Field(..., pattern=r"^https://t.me/.*")  # URL Telegram formatida bo‘lishi kerak
#     media: Optional[List[MediaPydantic]] = None

#     @validator("text")
#     def validate_text(cls, v):
#         if v and len(v) > 4096:  # Telegram xabar uzunligi chegarasi
#             raise ValueError("Xabar matni 4096 belgidan oshmasligi kerak")
#         return v





from pydantic import BaseModel, Field, validator
from typing import Optional, List

class MediaPydantic(BaseModel):
    file_type: str
    file_path: str
    file_size: Optional[int]

    class Config:
        from_attributes = True

class UserPydantic(BaseModel):
    id: int
    first_name: Optional[str]
    username: Optional[str]
    profile_photo: Optional[str]
    last_seen: Optional[str]
    is_bot: Optional[bool]

    class Config:
        from_attributes = True

class GroupPydantic(BaseModel):
    id: int  # gt=0 olib tashlandi, manfiy qiymatlarga ruxsat
    name: str
    username: Optional[str]  # @ shartsiz qoldirildi
    bio: Optional[str]
    member_count: Optional[int]
    created_at: Optional[str]
    profile_photo: Optional[str]

    @validator("username", pre=True, always=True)
    def add_at_prefix(cls, v):
        if v and not v.startswith("@"):
            return f"@{v}"
        return v

    class Config:
        orm_mode = True

class MessagePydantic(BaseModel):
    id: int
    group_id: int  # gt=0 olib tashlandi, manfiy qiymatlarga ruxsat
    user_id: Optional[int]
    account_name: str
    text: Optional[str]
    timestamp: str
    url: str
    group_name: Optional[str]
    group_username: Optional[str]
    group_bio: Optional[str]
    group_member_count: Optional[int]
    user_first_name: Optional[str]
    user_username: Optional[str]
    user_profile_photo: Optional[str]
    media: List[MediaPydantic] = []

    class Config:
        from_attributes = True
















































































# from sqlalchemy import Column, BigInteger, String, DateTime, TEXT
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class Message(Base):
#     __tablename__ = "messages"

#     id = Column(BigInteger, primary_key=True)
#     group_id = Column(BigInteger, nullable=False)
#     account_name = Column(String(50))
#     text = Column(TEXT)
#     timestamp = Column(DateTime(timezone=True))
#     url = Column(String(255))  # Xabar URL’si
#     user_id = Column(BigInteger)  # Foydalanuvchi IDsi
#     user_first_name = Column(String(100))  # Foydalanuvchi ismi
#     user_username = Column(String(100))  # Foydalanuvchi username’i (agar bo‘lsa)
#     user_profile_photo = Column(String(255), default="https://example.com/no-photo.jpg")  # Default rasm
#     group_profile_photo = Column(String(255), default="https://example.com/no-photo.jpg")  # Default rasm