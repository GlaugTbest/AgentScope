from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AGENTSCOPE_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("AGENTSCOPE_API_KEY", "test-key")
    from agentscope_api.main import create_app
    from agentscope_api.db import Base

    app = create_app()
    Base.metadata.create_all(app.state.engine) if hasattr(app.state, "engine") else None
    with TestClient(app) as test_client:
        Base.metadata.create_all(test_client.app.state.engine)
        yield test_client


@pytest.fixture()
def auth_headers():
    return {"Authorization": "Bearer test-key"}
