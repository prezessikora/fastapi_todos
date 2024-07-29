from tests.utils import *
from routers.auth import get_db, authenticate_user, create_access_token, get_current_user
from fastapi import status, HTTPException

from datetime import datetime, timedelta
from routers.auth import SECRET_KEY, ALGORITHM
from jose import jwt
import pytest
import pytz

app.dependency_overrides[get_db] = override_get_db

def test_auth_user(test_user):
    db = TestingSessionLocal()
    user = authenticate_user(test_user.username,'onyx', db)
    assert user != False
    assert user.username == test_user.username

def test_auth_wrong_user_name(test_user):
    pass

def test_auth_wrong_user_password(test_user):
    pass

def test_create_access_token():
        
    user = User(
        username = 'sikora',
        email = 'sikora@gmail.com',
        first_name = 'Kris',
        last_name = 'Sikora',
        hashed_password = b_crypt_context.hash('onyx'),
        role = 'admin',
        phone_number = '111-111-111'
    )

    exp = (datetime.now(pytz.utc) + timedelta(hours=1))

    token = create_access_token(user.username,1,"admin",timedelta(hours=1))
    decoded_token = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM],options={'verify_singnature': False})
        
    assert decoded_token['sub'] == user.username
    assert decoded_token['role'] == 'admin'
    assert decoded_token['id'] == 1
    
    token_exp = datetime.fromtimestamp(decoded_token['exp'],tz=pytz.utc)            
    # account for slight shift in datetime creation times
    exp = exp.replace(second=0,microsecond=0)
    token_exp = token_exp.replace(second=0,microsecond=0)
    assert token_exp == exp



@pytest.mark.asyncio
async def test_get_current_user_token():

    encode = {'sub': 'sikora', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)    
    user = await get_current_user(token=token)
    assert user == {'usermame': 'sikora', 'id': 1, 'role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():

    encode = {'role': 'admin'}
    token = jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)    
    
    
    try:
        user = await get_current_user(token=token)
    except HTTPException as excinfo:
        print(excinfo)
        assert excinfo.status_code == 401
        assert excinfo.detail == 'Authorization failed.'

    
        

    