from routers.admin import get_db,get_current_user
from fastapi import status

from models import Todo
from tests.utils import *

from main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



def test_read_all_auth(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    td = response.json()
    print(td)
    print(attrs)
    assert td[0].get('title') == attrs.get('title')


def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model is None, 'The todo with id: 1 was not deleted'


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todos/222")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
