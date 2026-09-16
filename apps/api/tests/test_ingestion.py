from copy import deepcopy


def batch():
    return {
        "trace": {
            "trace_id": "11111111-1111-4111-8111-111111111111",
            "agent_name": "demo",
            "start_time": "2026-09-16T12:00:00Z",
            "end_time": "2026-09-16T12:00:01Z",
            "status": "success",
            "metadata": {"source": "test"},
            "error": None,
        },
        "spans": [{
            "span_id": "22222222-2222-4222-8222-222222222222",
            "trace_id": "11111111-1111-4111-8111-111111111111",
            "parent_span_id": None,
            "type": "llm", "name": "plan",
            "start_time": "2026-09-16T12:00:00Z",
            "end_time": "2026-09-16T12:00:01Z", "status": "success",
            "input_tokens": 12, "output_tokens": 8, "estimated_cost": "0.000040000",
            "metadata": {}, "error": None,
        }],
    }


def test_ingest_is_atomic_and_idempotent(client, auth_headers):
    payload = batch()
    first = client.post("/v1/ingest", json=payload, headers=auth_headers)
    assert first.status_code == 201
    assert first.json() == {"trace_id": payload["trace"]["trace_id"], "span_count": 1, "created": True}
    again = client.post("/v1/ingest", json=payload, headers=auth_headers)
    assert again.status_code == 200
    assert again.json()["created"] is False
    altered = deepcopy(payload)
    altered["trace"]["agent_name"] = "other"
    assert client.post("/v1/ingest", json=altered, headers=auth_headers).status_code == 409


def test_ingest_rejects_invalid_parent_without_writing(client, auth_headers):
    payload = batch()
    payload["spans"][0]["parent_span_id"] = "33333333-3333-4333-8333-333333333333"
    assert client.post("/v1/ingest", json=payload, headers=auth_headers).status_code == 422
    assert client.get("/v1/traces", headers=auth_headers).json()["total"] == 0
