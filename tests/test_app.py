from http import HTTPStatus

from fastapi.testclient import TestClient

from to_do_list.app import app

client = TestClient(app)


def test_app_route_deve_retornar_ola_mundo():
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}
