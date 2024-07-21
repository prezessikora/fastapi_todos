from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, Path
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from models import Todo, User
from database import SessionLocal, engine
from starlette import status
from passlib.context import CryptContext

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dep = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
b_crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter(
    prefix='/users',
    tags=['users']
)

# this endpoint returns all information about the user that is currently logged in.
@router.get("/", status_code=status.HTTP_200_OK)
def get_user(user: user_dependency, db: db_dep):
    if (user is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Not authenticated')
    user_model = db.query(User).filter(User.id == user.get('id')).first()

    return user_model

class PasswordChangeRequest(BaseModel):
    password: str = Field(min_length=3)
    new_password: str=Field(min_length=3)

class PhoneChangeRequest(BaseModel):
    phone_number: str = Field(min_length=6)

# this endpoint should allow a user to change their current password.
@router.put('/password',status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dep, request: PasswordChangeRequest):
    if (user is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Not authenticated')
     
    user_model = db.query(User).filter(User.id == user.get('id')).first()        
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    if not b_crypt_context.verify(request.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Current password wrong')

    user_model.hashed_password = b_crypt_context.hash(request.new_password)

    db.add(user_model)
    db.commit()


@router.put('/phone',status_code=status.HTTP_204_NO_CONTENT)
async def change_phone(user: user_dependency, db: db_dep, phone_change_request: PhoneChangeRequest):
    if (user is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Not authenticated.')
    
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    user_model.phone_number = phone_change_request.phone_number
    db.add(user_model)
    db.commit()
    