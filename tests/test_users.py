from tests.utils import *
from routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/users/")
    response.status_code == status.HTTP_200_OK

    assert response.json()['username'] == 'sikora'
    assert response.json()['email'] == 'sikora@gmail.com'
    assert response.json()['first_name'] == 'Kris'
    assert response.json()['last_name'] == 'Sikora'
    assert response.json()['phone_number'] == '111-111-111'

def test_change_password_success(test_user):
    response = client.put('/users/password',json={
        'password' : 'onyx',
        'new_password' : 'xyzxyz',
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_password(test_user):
    response = client.put('/users/password',json={
        'password' : 'onyx1', 
        'new_password' : 'xyzxyz',
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED