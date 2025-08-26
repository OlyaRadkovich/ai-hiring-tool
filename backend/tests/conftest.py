import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    """
    Эта фикстура создает тестовый клиент для FastAPI, который мы можем
    использовать для отправки запросов к нашим эндпоинтам.
    'scope="module"' означает, что клиент будет создан один раз для всех тестов в модуле.
    """
    with TestClient(app) as c:
        yield c