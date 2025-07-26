from http import HTTPStatus

import factory
import factory.fuzzy
import pytest
from sqlalchemy import select

from to_do_list.models import Todo, TodoState, User


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        todo_data = {
            'title': 'Test todo',
            'description': 'Description test',
            'state': 'todo',
        }

        response = client.post(
            '/todos/',
            json=todo_data,
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Description test',
        'state': 'todo',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, user, client, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_by_title_should_return_1_todo(
    session, user, client, token
):
    expected_todos = 1
    todo = TodoFactory.create(user_id=user.id, title='Unique Title')
    session.add(todo)
    await session.commit()

    response = client.get(
        '/todos/?title=Unique%20Title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.json()['todos'][0]['title'] == 'Unique Title'


@pytest.mark.asyncio
async def test_list_todos_filter_by_state_should_return_2_todos(
    session, user, client, token
):
    expected_todos = 2
    session.add_all([
        TodoFactory.create(user_id=user.id, state=TodoState.todo),
        TodoFactory.create(user_id=user.id, state=TodoState.done),
        TodoFactory.create(user_id=user.id, state=TodoState.todo),
    ])
    await session.commit()

    response = client.get(
        '/todos/?state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    for todo in response.json()['todos']:
        assert todo['state'] == 'todo'


@pytest.mark.asyncio
async def test_list_todos_filter_by_description_should_return_1_todo(
    session, user, client, token
):
    expected_todos = 1
    todo = TodoFactory.create(
        user_id=user.id, description='Unique Description'
    )
    session.add(todo)
    await session.commit()

    response = client.get(
        '/todos/?description=Unique%20Description',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.json()['todos'][0]['description'] == 'Unique Description'


@pytest.mark.asyncio
async def test_delete_todo(session, user, client, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


@pytest.mark.asyncio
async def test_delete_todo_with_error(client, token):
    response = client.delete(
        f'/todos/{10}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_todo_error_other_user(client, user_2, session, token):
    todo_other_user = TodoFactory(user_id=user_2.id)
    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f'/todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_patch_todo(user, client, session, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'test1'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'test1'


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_fields(
    session, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'description': todo.description,
            'id': todo.id,
            'state': todo.state,
            'title': todo.title,
        }
    ]


@pytest.mark.asyncio
async def test_create_todo_error(session, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
