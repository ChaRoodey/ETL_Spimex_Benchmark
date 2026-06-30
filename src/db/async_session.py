import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.config import settings
from src.db.models import Base

async_engine = create_async_engine(settings.async_database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    logger.info("Initializing database")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        logging.info("Database initialized")
