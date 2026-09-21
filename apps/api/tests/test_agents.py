from .test_ingestion import batch
from .test_events import event


def test_trace_discovers_agent_with_origin_and_last_seen(client, auth_headers):
    payload = batch()
    payload["trace"]["agent_name"] = "trace-discovered"
    assert client.post("/v1/ingest", json=payload, headers=auth_headers).status_code == 201

    agent = client.get("/v1/agents", headers=auth_headers).json()["items"][0]
    assert agent["name"] == "trace-discovered"
    assert agent["registration_source"] == "discovered"
    assert agent["last_seen_at"] is not None


def test_events_discover_agent_and_manual_registration_claims_it(client, auth_headers):
    payload = event()
    payload["agent_name"] = "event-discovered"
    assert client.post("/v1/events", json={"events": [payload]}, headers=auth_headers).status_code == 201

    claimed = client.post("/v1/agents", json={"name": "event-discovered", "description": "Equipe de pesquisa"}, headers=auth_headers)
    assert claimed.status_code == 200
    assert claimed.json()["registration_source"] == "manual"
    assert claimed.json()["description"] == "Equipe de pesquisa"


def test_existing_manual_agent_name_remains_a_conflict(client, auth_headers):
    assert client.post("/v1/agents", json={"name": "manual"}, headers=auth_headers).status_code == 201
    assert client.post("/v1/agents", json={"name": "manual"}, headers=auth_headers).status_code == 409
