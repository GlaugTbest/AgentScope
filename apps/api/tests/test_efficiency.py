def setup_versions(client, headers):
    assert client.post('/v1/projects', headers=headers, json={'project_id': 'efficiency', 'name': 'Efficiency'}).status_code == 201
    agent = client.post('/v1/agents', headers=headers, json={'name': 'optimizer'}).json()
    for version in ('baseline', 'variant'):
        assert client.post('/v1/agent-versions', headers=headers, json={'agent_version_id': version, 'agent_id': agent['agent_id'], 'project_id': 'efficiency'}).status_code == 201


def test_simulated_prices_evaluations_and_evidence_based_experiment(client, auth_headers):
    setup_versions(client, auth_headers)
    created = client.post('/v1/prices', headers=auth_headers, json={'catalog_id': 'local-qwen', 'model': 'qwen3:4b', 'provider': 'ollama', 'input_per_million_nano_usd': 100000000, 'output_per_million_nano_usd': 200000000, 'simulated': True})
    assert created.status_code == 201
    estimate = client.get('/v1/prices/local-qwen/estimate?input_tokens=1000&output_tokens=500', headers=auth_headers).json()
    assert estimate['simulated'] is True
    assert estimate['estimated_cost_nano_usd'] == 200000
    evaluation = client.post('/v1/evaluations', headers=auth_headers, json={'evaluation_id': 'eval-1', 'project_id': 'efficiency', 'agent_version_id': 'variant', 'criterion': 'grounded', 'score': 0.9, 'passed': True, 'evidence': {'expected_sources': ['DOC-03']}})
    assert evaluation.status_code == 201
    assert client.get('/v1/evaluations?project_id=efficiency', headers=auth_headers).json()['total'] == 1
    experiment = client.post('/v1/experiments', headers=auth_headers, json={'experiment_id': 'exp-1', 'project_id': 'efficiency', 'baseline_version_id': 'baseline', 'variant_version_id': 'variant', 'baseline': [{'quality': 0.90, 'input_tokens': 1000, 'output_tokens': 500, 'latency_ms': 800}], 'variant': [{'quality': 0.88, 'input_tokens': 600, 'output_tokens': 300, 'latency_ms': 700}]})
    assert experiment.status_code == 201
    result = experiment.json()
    assert result['recommendation'] == 'adopt_variant'
    assert result['deltas']['tokens'] == -600
    assert result['evidence']['quality_threshold'] == 0.05
