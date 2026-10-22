"""Shared test setup.

Every test talks to the app over HTTP. Behind the app is a real PostgreSQL
test database whose tables come from the Alembic migrations.
"""

import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.main import app
from tests.database import TEST_DATABASE_URL, run_sql

# Point the app and Alembic at the test database, never the development one.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
# Skip the placeholder's pretend waiting, so the tests run in seconds.
os.environ["PLACEHOLDER_STEP_SECONDS"] = "0"


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
