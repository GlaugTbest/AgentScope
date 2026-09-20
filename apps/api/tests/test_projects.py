def test_projects_can_be_created_and_listed(client, auth_headers):
    created = client.post('/v1/projects', headers=auth_headers, json={'project_id': 'research', 'name': 'Research', 'description': 'Local research agents'})
    assert created.status_code == 201
    assert created.json()['project_id'] == 'research'
    assert client.post('/v1/projects', headers=auth_headers, json={'project_id': 'research', 'name': 'Other'}).status_code == 409
    listed = client.get('/v1/projects', headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()['items'][0]['name'] == 'Research'
