from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from to_do_list.schemas import (
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def app_route():
    return {'message': 'Olá Mundo!'}


@app.get('/app', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def html_route():
    return """
    <html>
        <head>
            <title>Olá mundo!</title>
        </head>
        <body>
            <h1>Olá Mundo</h1>
        </body>
    </html>
    """


@app.post('/user/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)

    return user_with_id


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users():
    return {'users': database}
