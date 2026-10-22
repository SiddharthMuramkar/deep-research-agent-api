"""How a Run ends when its work goes wrong, or when a restart cuts it off.

The first test swaps the work behind `start_run` (the second seam). Every
test checks the result through the HTTP endpoints, like a caller would.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app import runs
from app.main import app
from app.tables import RunStatus
from tests.database import run_sql


def test_a_run_whose_work_raises_ends_failed_with_the_error(client, monkeypatch):
    async def broken_research(query, update_status):
        await update_status(RunStatus.planning)
        raise RuntimeError("the search engine is down")

    monkeypatch.setattr(runs, "research", broken_research)

    run_id = client.post("/research/query", json={"query": "Anything"}).json()["run_id"]
    body = client.get(f"/research/{run_id}/status").json()

    assert body["status"] == "failed"
    assert body["error"] == "RuntimeError: the search engine is down"


@pytest.mark.parametrize("status", ["queued", "planning", "running"])
def test_starting_the_service_fails_runs_cut_off_by_a_restart(status):
    run_id = uuid.uuid4()
    run_sql(
        "INSERT INTO runs (id, query, status) VALUES (:id, 'Anything', :status)",
        id=run_id,
        status=status,
    )

    with TestClient(app) as client:
        body = client.get(f"/research/{run_id}/status").json()

    assert body["status"] == "failed"
    assert body["error"] == "interrupted by restart"


def test_starting_the_service_leaves_finished_runs_alone():
    run_id = uuid.uuid4()
    run_sql(
        "INSERT INTO runs (id, query, status) VALUES (:id, 'Anything', 'done')",
        id=run_id,
    )

    with TestClient(app) as client:
        body = client.get(f"/research/{run_id}/status").json()

    assert body["status"] == "done"
    assert body["error"] is None
