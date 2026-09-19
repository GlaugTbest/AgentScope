from copy import deepcopy


def event(event_id="evt-1", kind="execution.started", occurred_at="2026-09-18T12:00:00Z"):
    return {
        "event_id": event_id, "schema_version": "1.0", "type": kind, "source": "sdk-python",
        "project_id": "local", "agent_name": "researcher", "agent_id": "agent-1",
        "instance_id": "worker-1", "execution_id": "run-1", "task_id": "task-1",
        "occurred_at": occurred_at, "payload": {"message": "started"},
    }


def test_events_create_open_execution_and_are_idempotent(client, auth_headers):
    payload = {"events": [event()]}
    first = client.post("/v1/events", json=payload, headers=auth_headers)
    assert first.status_code == 201
    assert first.json() == {"accepted": 1, "duplicate": 0}
    again = client.post("/v1/events", json=payload, headers=auth_headers)
    assert again.status_code == 200
    assert again.json() == {"accepted": 0, "duplicate": 1}
    execution = client.get("/v1/executions/run-1", headers=auth_headers).json()
    assert execution["execution"]["state"] == "executing"
    assert execution["events"][0]["event_id"] == "evt-1"


def test_terminal_execution_does_not_reopen_from_old_event(client, auth_headers):
    completed = event("evt-2", "execution.completed", "2026-09-18T12:00:02Z")
    started = event("evt-1", "execution.started", "2026-09-18T12:00:00Z")
    assert client.post("/v1/events", json={"events": [completed]}, headers=auth_headers).status_code == 201
    assert client.post("/v1/events", json={"events": [started]}, headers=auth_headers).status_code == 201
    assert client.get("/v1/executions/run-1", headers=auth_headers).json()["execution"]["state"] == "completed"


def test_event_conflict_is_explicit(client, auth_headers):
    payload = {"events": [event()]}
    client.post("/v1/events", json=payload, headers=auth_headers)
    conflict = deepcopy(payload)
    conflict["events"][0]["payload"] = {"message": "different"}
    assert client.post("/v1/events", json=conflict, headers=auth_headers).status_code == 409
