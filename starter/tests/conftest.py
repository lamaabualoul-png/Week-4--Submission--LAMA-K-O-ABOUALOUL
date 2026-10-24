import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Give every test its own empty database so tests are order-independent."""
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "test_links.db")
    main.init_db()


@pytest.fixture
def client():
    return TestClient(main.app)
