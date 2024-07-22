from routers.todos import get_db,get_current_user
from fastapi.testclient import TestClient
from fastapi import status

from models import Todo
from tests.utils import *
from main import app


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 
                                'description': 'so that you are a better manager :)', 
                                'id': 1, 
                                'owner_id': 1, 
                                'title': 'Lear to code',
                                'priority' : 5
                                }]
    
def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 
                                'description': 'so that you are a better manager :)', 
                                'id': 1, 
                                'owner_id': 1, 
                                'title': 'Lear to code',
                                'priority' : 5
                                }
    
def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todos/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'Todo not found'}

def test_create_todo():
    request_data = {        
        'title': 'Lear to code',
        'description': 'so that you are a better manager ',
        'priority' : 2,
        'complete': False,
    }
    response = client.post("/todo/",json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model.title == request_data.get('title')


def test_update_todo(test_todo):
    request_data = {        
        'title': 'Learn to code changed',
        'description': 'abc',
        'priority': 1,
        'complete': False
    }


    response = client.put("/todo/1",json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model.title == request_data.get('title')
    

def test_delete_todo(test_todo):

    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model is None
    