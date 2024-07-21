from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, Path
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from models import Todo
from database import SessionLocal, engine
from starlette import status
from pymongo import MongoClient

URL = "mongodb://sikora:sikora@localhost:27017/"
client = MongoClient(URL)
mongo_db = client.messaging

router = APIRouter(
    prefix='/messaging',
    tags=['messaging']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# signup (full name, username, password, profile image) -> auth_token, user_id
# login (username, password) -> auth_token, user_id
# user_search(username) -> user_id


class MessageRequest(BaseModel):    
    recipient_id: int
    text: str    

class ChannelCreateRequest(BaseModel):
    pass

# -> User home page, channels, group chats, DMs
@router.get('/homepage', status_code=status.HTTP_200_OK)
async def get_homepage(user: user_dependency, db: db_dep):
    if (user is None):
        raise HTTPException('Authentication failed.')

    return {'result': 'homepage'}

from datetime import datetime

# -> group chat id
@router.post("/send_message/", status_code=status.HTTP_201_CREATED)
async def send_message(user: user_dependency, db: db_dep, message: MessageRequest):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')
    # create group_chat if does not exist
    chat_id = mongo_db.chats.insert_one({'created': datetime.now()}).inserted_id.__str__()
    # add group_chat participants
    mongo_db.participants.insert_many([{'user_id': user['id'], 'chat_id' : chat_id},{'user_id': message.recipient_id, 'chat_id' : chat_id}])
    # store message
    result = mongo_db.messages.insert_one({'from': user['id'], 'chat_id': chat_id, 'message': message.text})
    
    # TODO send message to the SQS queue

    return {'message_id': result.inserted_id.__str__()}

@router.get("/find_user/{user_name}")
async def send_message(user: user_dependency, db: db_dep,  user_name: str):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')
    
    return {'result': 'message sent'}

@router.post("/send_message/{channel_id}", status_code=status.HTTP_201_CREATED)
async def send_message(user: user_dependency, db: db_dep,  channel_id: int, message: MessageRequest):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')
    return {'result': 'message sent'}


@router.post("/create_channel", status_code=status.HTTP_201_CREATED)
async def create_channel(user: user_dependency, db: db_dep, request: ChannelCreateRequest):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')

    return {'result': 'channel created'}


@router.put("/join_channel/{channel_id}", status_code=status.HTTP_200_OK)
async def join_channel(user: user_dependency, db: db_dep, channel_id: int):
    if (user is None):
        raise HTTPException(status_code=401, detail='Authentication failed.')

    return {'result': 'user joined channel'}

