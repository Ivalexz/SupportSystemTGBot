from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from model.roles.User import User
from model.services.TicketRequest import TicketRequest
from model.services.StatusUpdate import StatusUpdate
from app.auth import create_access_token, get_current_manager
from typing import Dict
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str
    role: str = "user"

app = FastAPI()

users_list =[]
request_list=[]
comment_list=[]
msg_list =[]

request_id_counter = 1
msg_id_counter = 1

@app.get("/")
def home():
    return {"message": "App in working"}

@app.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for usr in users_list:
        if usr["user_tg_id"] == int(data.username):
            user = usr
            break

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    token = create_access_token(user["user_tg_id"], user["role"])
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users/register")
def register_user(data: RegisterRequest):
    for usr in users_list:
        if usr["user_tg_id"] == str(data.telegram_id):
            return {"message": "User already exists"}

    users_list.append({
        "user_id": len(users_list) + 1,
        "user_tg_id": str(data.telegram_id),
        "username": data.username or data.full_name,
        "role": data.role
    })
    return {"message": "Registered successfully"}

@app.get("/users/by-telegram/{telegram_id}")
def get_user(telegram_id: int):
    user = None
    for usr in users_list:
        if usr["user_tg_id"] == str(telegram_id):
            user = usr
            break

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@app.post("/requests")
def create_request(data: TicketRequest):
    global request_id_counter
    user = None
    for usr in users_list:
        if usr["user_tg_id"] == str(data.telegram_id):
            user = usr
            break

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    req = {
        "id": request_id_counter,
        "user_tg_id": data.telegram_id,
        "title": data.title,
        "description": data.description,
        "status": "New"
    }
    request_list.append(req)
    request_id_counter += 1
    return {"message": "Request created", "request": req}


@app.get("/requests/user/{telegram_id}")
def get_user_requests(telegram_id: int):
    user = None
    for usr in users_list:
        if usr["user_tg_id"] == str(telegram_id):
            user = usr
            break

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reqs = [r for r in request_list if r["user_tg_id"] == telegram_id]
    return {"requests": reqs}

@app.patch("/requests/{req_id}/status")
def update_status(req_id: int, data: StatusUpdate, current_user: Dict = Depends(get_current_manager)):
    req = None
    for r in request_list:
        if r["id"] == req_id:
            req = r
            break

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req["status"] = data.status

    add_msg(req["user_tg_id"], req_id, data.status,
                      f"Статус заявки #{req_id} змінено на {data.status}")
    return {"message": "Status updated", "request": req}


@app.get("/notifications/{telegram_id}")
def get_msgs(telegram_id: int):
    messages = []
    for m in msg_list:
        if m["user_tg_id"] == telegram_id:
            messages.append(m)

    return {"notifications": messages}


def add_msg(telegram_id: int, request_id: int, status: str, text: str):
    global msg_id_counter
    msg_list.append({
        "id": msg_id_counter,
        "user_tg_id": telegram_id,
        "request_id": request_id,
        "status": status,
        "text": text
    })
    msg_id_counter += 1