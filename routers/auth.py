from datetime import datetime, timedelta
import string
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '18bb16ceebedc345a7bacae366db100232814b2e9db0031ce7601d40d857bf0f'
ALGORITHM = 'HS256'

b_crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dep, request: CreateUserRequest):
    model = User(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=b_crypt_context.hash(request.password),
        role=request.role,
        username=request.username,
        is_active=True,
        phone_number = request.phone
    )
    db.add(model)
    db.commit()
    return model


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY,
                             algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if (username is None or user_id is None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed.')
        return {'usermame': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed.')


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if (user is not None):
        print(f'User {username} found.')
        if b_crypt_context.verify(password, user.hashed_password):
            return user
        else:
            return False
    else:
        print(f'User {username} NOT found.')
        return False


def create_access_token(username: string, user_id: int, role: string, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dep):
    user = authenticate_user(form_data.username, form_data.password, db)
    if (not user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization failed.')
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token':  token, 'token_type': 'bearer'}
