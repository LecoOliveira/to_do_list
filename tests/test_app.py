from http import HTTPStatus

from to_do_list.schemas import UserPublic
from to_do_list.security import create_access_token


def test_create_user(client):
    response = client.post(
        '/users/',
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


def test_create_user_username_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'test@mail.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': user.email,
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_list_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_get_user(client, user):
    responde = client.get(f'/users/{user.id}')

    assert responde.status_code == HTTPStatus.OK
    assert responde.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_get_user_not_found(client):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'new_username',
            'email': 'test@email.com',
            'password': 'new_password',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'new_username',
        'email': 'test@email.com',
    }


def test_update_user_without_permissions(client, user, user_2, token):
    response = client.put(
        f'/users/{user_2.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'new_username',
            'email': 'test@email.com',
            'password': 'new_password',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_if_user_exists(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'alex',
            'email': 'test@email.com',
            'password': 'password',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'alex',
            'email': 'test@email.com',
            'password': 'password',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_without_permission(client, user, user_2, token):
    response = client.delete(
        f'/users/{user_2.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'bearer'


def test_get_token_incorrect_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'password_incorrect',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_get_token_incorrect_username(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'incorrect_username',
            'password': user.password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_get_current_user_error(client):
    fake_data = {'test': 'test'}
    token = create_access_token(fake_data)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_found(client, token):
    fake_data = {'sub': 'test@test'}
    token = create_access_token(fake_data)

    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
