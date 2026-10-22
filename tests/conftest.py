"""Shared test setup.

Every test talks to the app over HTTP. Behind the app is a real PostgreSQL
test database whose tables come from the Alembic migrations.
"""

import asyncio
import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.main import app

TEST_DATABASE_URL = (
    "postgresql+asyncpg://research:research@localhost:5432/research_test"
)

# Point the app and Alembic at the test database, never the development one.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


def run_sql(sql: str, **params: object) -> None:
    """Run one SQL statement against the test database, for test setup only."""

    async def run() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as connection:
            await connection.execute(text(sql), params)
        await engine.dispose()

    asyncio.run(run())


@pytest.fixture(scope="session", autouse=True)
def database() -> None:
    """Rebuild the test database from the migrations, once per test session."""
    alembic = Config("alembic.ini")
    command.downgrade(alembic, "base")
    command.upgrade(alembic, "head")


@pytest.fixture(autouse=True)
def empty_runs_table(database: None) -> None:
    run_sql("TRUNCATE runs")


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
