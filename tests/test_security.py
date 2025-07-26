from http import HTTPStatus

from freezegun import freeze_time
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


def test_token_expired_after_time(client, user):
    with freeze_time('2025-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wronguser',
                'email': 'wrong@email',
                'password': 'wrongpass',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
