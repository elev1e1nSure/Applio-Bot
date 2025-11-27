"""
Database initialization and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import DB_FILE
from db.models import Base

# SQLite async engine
DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE}"
engine = create_async_engine(DATABASE_URL, echo=False)

# Async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get async database session."""
    async with async_session() as session:
        yield session

