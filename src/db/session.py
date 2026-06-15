import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.db.models import Base

engine = create_async_engine(f'postgresql+asyncpg://spimex_user:spimex@localhost:5532/spimex_db', echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
