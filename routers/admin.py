from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, Path
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from models import Todo
from database import SessionLocal, engine
from starlette import status

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dep = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def checkUserIsAdmin(user):
    if user is None or user.get('role') != 'admin':
        reason = 'Not logged in.'
        if user.get('role') != 'admin':
            reason = 'Not admin.'
        raise HTTPException(status_code=401, detail=f'Authentication failed: {reason}')


@router.get('/todos', status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dep):
    checkUserIsAdmin(user)
    return db.query(Todo).filter().all()

@router.delete('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_todos(todo_id: int, user: user_dependency, db: db_dep):
    checkUserIsAdmin(user)

    model = db.query(Todo).filter(todo_id == Todo.id).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()


 