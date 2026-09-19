def test_error_demo_marks_the_trace_as_error(client, auth_headers):
    agent = client.post('/v1/agents', headers=auth_headers, json={'name': 'failure-demo'}).json()

    response = client.post(f"/v1/agents/{agent['agent_id']}/demo?scenario=error", headers=auth_headers)

    assert response.status_code == 201
    detail = client.get(f"/v1/traces/{response.json()['trace_id']}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()['trace']['status'] == 'error'
    assert detail.json()['trace']['error']['type'] == 'TimeoutError'
