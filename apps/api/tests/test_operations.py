from .test_ingestion import batch


def test_trace_export_is_sanitized_and_retention_deletes_related_spans(client, auth_headers):
    payload = batch(); payload['trace']['metadata'] = {'token': 'secret', 'safe': 'kept'}; payload['spans'][0]['metadata'] = {'authorization': 'Bearer hidden'}
    child = dict(payload['spans'][0]); child.update({'span_id': '00000000-0000-0000-0000-000000000099', 'parent_span_id': payload['spans'][0]['span_id'], 'name': 'child span'})
    payload['spans'].append(child)
    assert client.post('/v1/ingest', headers=auth_headers, json=payload).status_code == 201
    exported = client.get(f"/v1/traces/{payload['trace']['trace_id']}/export", headers=auth_headers)
    assert exported.json()['trace']['metadata']['token'] == '[REDACTED]'
    assert exported.json()['spans'][0]['metadata']['authorization'] == '[REDACTED]'
    deleted = client.delete('/v1/operations/retention?before=2026-09-17T00:00:00Z', headers=auth_headers)
    assert deleted.json() == {'deleted_traces': 1, 'deleted_spans': 2}
    assert client.get(f"/v1/traces/{payload['trace']['trace_id']}", headers=auth_headers).status_code == 404
