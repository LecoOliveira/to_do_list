from http import HTTPStatus

from to_do_list.schemas import UserPublic


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


def test_create_user_username_exists(client, user):
    response = client.post(
        '/user/',
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
        '/user/',
        json={
            'username': 'test',
            'email': user.email,
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_list_users_without_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_list_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

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


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'new_username',
            'email': 'new@email.com',
            'password': 'new_password',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'new_username',
        'email': 'new@email.com',
    }


def test_update_user_not_found(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'new_username',
            'email': 'test@email.com',
            'password': 'new_password',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_if_user_exists(client, user):
    client.post(
        '/user',
        json={
            'username': 'alex',
            'email': 'test@email.com',
            'password': 'password',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
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


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
