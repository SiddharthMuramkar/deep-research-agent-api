"""The research API, tested from the outside: requests in, responses out."""

import uuid

import pytest


def submit(client, query="What is a tracer bullet?"):
    return client.post("/research/query", json={"query": query})


def test_submitting_a_query_returns_202_with_a_queued_run(client):
    response = submit(client)

    assert response.status_code == 202
    body = response.json()
    # Version 4 UUIDs are random, so nobody can guess another caller's run ID.
    assert uuid.UUID(body["run_id"]).version == 4
    assert body["status"] == "queued"


def test_a_submitted_run_reaches_done_on_its_own(client):
    # The test client waits for the background work, and the tests set the
    # placeholder's waits to zero, so the Run is finished by the time we look.
    run_id = submit(client).json()["run_id"]

    response = client.get(f"/research/{run_id}/status")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == run_id
    assert body["status"] == "done"
    assert body["error"] is None
    assert body["created_at"]
    assert body["updated_at"]


def test_looking_up_an_unknown_run_returns_404(client):
    response = client.get(f"/research/{uuid.uuid4()}/status")

    assert response.status_code == 404
    assert response.json() == {"detail": "Run not found"}


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"query": ""},
        {"query": "   "},
        {"query": "x" * 2001},
    ],
    ids=["missing", "empty", "blank", "too-long"],
)
def test_an_invalid_query_is_rejected_with_422_naming_the_field(client, body):
    response = client.post("/research/query", json=body)

    assert response.status_code == 422
    assert [error["loc"] for error in response.json()["detail"]] == [["body", "query"]]


def test_a_query_of_exactly_2000_characters_is_accepted(client):
    assert submit(client, query="x" * 2000).status_code == 202
