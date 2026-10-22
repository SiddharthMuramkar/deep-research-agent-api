"""The test database, and a helper for setting it up directly."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_URL = (
    "postgresql+asyncpg://research:research@localhost:5432/research_test"
)


def run_sql(sql: str, **params: object) -> None:
    """Run one SQL statement against the test database, for test setup only."""

    async def run() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as connection:
            await connection.execute(text(sql), params)
        await engine.dispose()

    asyncio.run(run())
