from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)