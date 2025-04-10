import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
from src.models import Base  # Sizning modellaringiz joylashgan fayl

# Alembic konfiguratsiyasini olish
config = context.config

# Logging sozlamalari
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Databaza URL’ni `alembic.ini` dan olish
sqlalchemy_url = config.get_main_option("sqlalchemy.url")

# Asinxron dvigatel yaratish
connectable = create_async_engine(sqlalchemy_url, echo=True)

def run_migrations_offline():
    """Offline migratsiyalarni ishga tushirish"""
    raise RuntimeError("Offline mode is not supported with async engines in this setup.")

async def run_migrations_online():
    """Online migratsiyalarni asinxron tarzda ishga tushirish"""
    async with connectable.connect() as connection:  # Asinxron ulanish
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Migratsiyalarni sinxron tarzda bajarish"""
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        render_as_batch=True
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())