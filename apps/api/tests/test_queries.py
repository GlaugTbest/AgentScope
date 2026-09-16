from .test_ingestion import batch


def test_list_summary_and_detail_expose_aggregates(client, auth_headers):
    payload = batch()
    assert client.post("/v1/ingest", json=payload, headers=auth_headers).status_code == 201
    listing = client.get("/v1/traces?span_type=llm", headers=auth_headers).json()
    assert listing["total"] == 1
    assert listing["items"][0]["total_tokens"] == 20
    assert listing["items"][0]["estimated_cost"] == "0.000040000"
    summary = client.get("/v1/traces/summary", headers=auth_headers).json()
    assert summary["total_traces"] == 1
    assert summary["success_rate"] == 1.0
    detail = client.get(f"/v1/traces/{payload['trace']['trace_id']}", headers=auth_headers).json()
    assert detail["trace"]["span_count"] == 1
    assert detail["spans"][0]["name"] == "plan"
