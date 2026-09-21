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


def test_latency_percentiles_use_the_recorded_trace_samples(client, auth_headers):
    first = batch(); first["trace"]["end_time"] = "2026-09-16T12:00:00.100Z"; first["spans"][0]["end_time"] = first["trace"]["end_time"]
    second = batch(); second["trace"]["trace_id"] = "22222222-2222-4222-8222-222222222222"; second["spans"][0]["trace_id"] = second["trace"]["trace_id"]; second["spans"][0]["span_id"] = "33333333-3333-4333-8333-333333333333"; second["trace"]["end_time"] = "2026-09-16T12:00:01Z"
    assert client.post("/v1/ingest", json=first, headers=auth_headers).status_code == 201
    assert client.post("/v1/ingest", json=second, headers=auth_headers).status_code == 201
    metrics = client.get("/v1/metrics/latency", headers=auth_headers).json()
    assert metrics == {"sample_size": 2, "p50_ms": 100, "p95_ms": 1000, "p99_ms": 1000}
