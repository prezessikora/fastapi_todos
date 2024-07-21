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


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=5)
    complete: bool


@router.get('/todos', status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dep):
    if (user is None):
        raise HTTPException('Authentication failed.')

    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()


@router.get('/todos/{todo_id}', status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dep, todo_id: int = Path(gt=0)):
    if (user is None):
        raise HTTPException('Authentication failed.')
    model = db.query(Todo).filter(Todo.id == todo_id).filter(
        Todo.owner_id == user.get('id')).first()
    if (model is not None):
        return model
    raise HTTPException(status_code=404, detail='Todo not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dep, todo_request: TodoRequest):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')
    model = Todo(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dep, todo_id: int, todo_request: TodoRequest):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')

    model = db.query(Todo).filter(Todo.id == todo_id).filter(
        Todo.owner_id == user.get('id')).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    model.complete = todo_request.complete
    model.description = todo_request.description
    model.priority = todo_request.priority
    model.title = todo_request.title

    db.add(model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user: user_dependency, db: db_dep, todo_id: int):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')

    model = db.query(Todo).filter(Todo.id == todo_id).filter(
        Todo.owner_id == user.get('id')).first()
    if model == None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
