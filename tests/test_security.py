from http import HTTPStatus

from jwt import decode

from to_do_list.security import create_access_token


def test_jwt(settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalid_token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }
