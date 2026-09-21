def test_versions_instances_and_tasks_are_project_scoped_and_paginated(client, auth_headers):
    assert client.post('/v1/projects', headers=auth_headers, json={'project_id': 'p1', 'name': 'Project one'}).status_code == 201
    agent = client.post('/v1/agents', headers=auth_headers, json={'name': 'writer'}).json()
    version = client.post('/v1/agent-versions', headers=auth_headers, json={'agent_version_id': 'writer-v1', 'agent_id': agent['agent_id'], 'project_id': 'p1', 'reference': 'git:abc'} )
    assert version.status_code == 201
    instance = client.post('/v1/instances', headers=auth_headers, json={'instance_id': 'writer-worker-1', 'project_id': 'p1', 'agent_id': agent['agent_id'], 'agent_version_id': 'writer-v1', 'runtime': 'python'})
    assert instance.status_code == 201
    assert client.get('/v1/instances?project_id=p1', headers=auth_headers).json()['items'][0]['runtime'] == 'python'
    for number in range(2):
        assert client.post('/v1/tasks', headers=auth_headers, json={'task_id': f'task-{number}', 'project_id': 'p1', 'title': f'Task {number}'}).status_code == 201
    page = client.get('/v1/tasks?project_id=p1&limit=1&offset=1', headers=auth_headers).json()
    assert page['total'] == 2
    assert len(page['items']) == 1


def test_delegations_link_executions_and_are_paginated(client, auth_headers):
    events = [
        {'event_id': 'source-start', 'type': 'execution.started', 'source': 'test', 'agent_name': 'coordinator', 'execution_id': 'source', 'occurred_at': '2026-09-16T12:00:00Z'},
        {'event_id': 'target-start', 'type': 'execution.started', 'source': 'test', 'agent_name': 'researcher', 'execution_id': 'target', 'occurred_at': '2026-09-16T12:00:01Z'},
    ]
    assert client.post('/v1/events', headers=auth_headers, json={'events': events}).status_code == 201
    created = client.post('/v1/delegations', headers=auth_headers, json={'delegation_id': 'delegate-1', 'source_execution_id': 'source', 'target_execution_id': 'target', 'occurred_at': '2026-09-16T12:00:02Z', 'metadata': {'reason': 'research'}})
    assert created.status_code == 201
    page = client.get('/v1/delegations?limit=1&offset=0', headers=auth_headers).json()
    assert page['total'] == 1
    assert page['items'][0]['source_execution_id'] == 'source'
    assert page['items'][0]['metadata']['reason'] == 'research'
