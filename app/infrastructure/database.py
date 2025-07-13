from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


async_engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


sync_engine = create_engine(settings.database_url.replace("+asyncpg", ""))
SyncSession = sessionmaker(sync_engine)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session