import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app


def test_the_service_refuses_to_start_without_a_database_url(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL")
    monkeypatch.chdir(tmp_path)  # an empty folder, so there is no .env file either

    with pytest.raises(ValidationError, match="database_url"), TestClient(app):
        pass
