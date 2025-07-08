from sqlalchemy import select

from to_do_list.models import User


def test_create_user(session):
    new_user = User(
        username='testuser',
        email='test@test.com',
        password='password123',
    )

    session.add(new_user)
    session.commit()
    user = session.scalar(select(User).where(User.username == 'testuser'))

    assert user.username == 'testuser'
    assert user.email == 'test@test.com'
    assert user.password == 'password123'
