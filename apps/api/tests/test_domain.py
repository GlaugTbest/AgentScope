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
