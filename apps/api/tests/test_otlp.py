def test_otlp_http_json_preserves_opaque_ids_and_genai_attributes(client, auth_headers):
    payload = {"resourceSpans": [{"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "otlp-worker"}}]}, "scopeSpans": [{"spans": [{"traceId": "0123456789abcdef0123456789abcdef", "spanId": "0123456789abcdef", "name": "chat", "startTimeUnixNano": "1760000000000000000", "endTimeUnixNano": "1760000001000000000", "attributes": [{"key": "gen_ai.request.model", "value": {"stringValue": "qwen3:4b"}}, {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "12"}}], "status": {"code": 1}}]}]}]}
    response = client.post('/v1/otlp/v1/traces', headers=auth_headers, json=payload)
    assert response.status_code == 200
    assert response.json()['traces'] == ['0123456789abcdef0123456789abcdef']
    trace = client.get('/v1/traces/0123456789abcdef0123456789abcdef', headers=auth_headers).json()
    assert trace['spans'][0]['span_id'] == '0123456789abcdef'
    assert trace['spans'][0]['model'] == 'qwen3:4b'
