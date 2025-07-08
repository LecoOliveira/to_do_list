from http import HTTPStatus


def test_app_route_deve_retornar_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_deve_retornar_um_html(client):
    response = client.get('/app')

    assert response.status_code == HTTPStatus.OK
    assert 'Olá Mundo' in response.text


def test_create_user_deve_criar_um_usuario(client):
    response = client.post(
        '/user/',
        json={
            'username': 'alex',
            'email': 'alex@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alex',
        'email': 'alex@email.com',
    }
