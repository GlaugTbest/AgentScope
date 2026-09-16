def test_health_is_public_and_checks_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_read_routes_require_exact_bearer_key(client, auth_headers):
    assert client.get("/v1/traces").status_code == 401
    assert client.get("/v1/traces", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/v1/traces", headers=auth_headers).status_code == 200


def test_agents_can_be_created_listed_and_run_a_real_demo(client, auth_headers):
    created = client.post(
        "/v1/agents", json={"name": "product-researcher", "description": "Synthetic test agent"}, headers=auth_headers
    )
    assert created.status_code == 201
    agent = created.json()
    assert client.get("/v1/agents", headers=auth_headers).json()["items"][0]["name"] == "product-researcher"
    demo = client.post(f"/v1/agents/{agent['agent_id']}/demo", headers=auth_headers)
    assert demo.status_code == 201
    assert demo.json()["span_count"] == 4
    assert client.get("/v1/traces?agent_name=product-researcher", headers=auth_headers).json()["total"] == 1
