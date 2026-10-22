"""The database connection, shared by the endpoints and the background work."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

# Keeps a pool of open connections to PostgreSQL. It only connects when the
# first query runs, so creating it here is cheap.
engine = create_async_engine(settings.database_url)

# `async with new_session() as session:` opens one conversation with the database.
new_session = async_sessionmaker(engine, expire_on_commit=False)
