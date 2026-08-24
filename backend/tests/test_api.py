from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_create_game_endpoint() -> None:
    response = client.post('/api/games', json={'player_name': 'alice', 'session_token': 'session-1'})
    assert response.status_code == 200
    assert len(response.json()['code']) == 5


def test_join_game_endpoint() -> None:
    created = client.post('/api/games', json={'player_name': 'alice', 'session_token': 'session-1'}).json()
    response = client.post('/api/games/join', json={'code': created['code'], 'player_name': 'bob', 'session_token': 'session-2'})
    assert response.status_code == 200
    assert response.json()['code'] == created['code']
