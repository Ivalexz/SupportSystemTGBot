from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List
from pydantic import BaseModel
from app.auth import create_access_token, get_current_manager



class RegisterRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str
    role: str = "client"

class TicketRequest(BaseModel):
    telegram_id: int
    title: str
    description: str

class StatusUpdate(BaseModel):
    status: str



app = FastAPI()

users_list: List[Dict] = []
request_list: List[Dict] = []
msg_list: List[Dict] = []

request_id_counter = 1
msg_id_counter = 1


@app.get("/")
def home():
    return {"message": "App is working"}

@app.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    user = next((usr for usr in users_list if usr["user_tg_id"] == int(data.username)), None)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    token = create_access_token(user["user_tg_id"], user["role"])
    return {"access_token": token, "token_type": "bearer"}


@app.post("/users/register")
def register_user(data: RegisterRequest):
    if any(usr["user_tg_id"] == data.telegram_id for usr in users_list):
        return {"message": "User already exists"}

    users_list.append({
        "user_id": len(users_list) + 1,
        "user_tg_id": data.telegram_id,
        "username": data.username or data.full_name,
        "full_name": data.full_name,
        "role": data.role
    })
    return {"message": "Registered successfully"}

@app.get("/users/by-telegram/{telegram_id}")
def get_user(telegram_id: int):
    user = next((usr for usr in users_list if usr["user_tg_id"] == telegram_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/requests")
def create_request(data: TicketRequest):
    global request_id_counter
    user = next((usr for usr in users_list if usr["user_tg_id"] == data.telegram_id), None)
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
    user = next((usr for usr in users_list if usr["user_tg_id"] == telegram_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reqs = [r for r in request_list if r["user_tg_id"] == telegram_id]
    return {"requests": reqs}

@app.patch("/requests/{req_id}/status")
def update_status(req_id: int, data: StatusUpdate, current_user: Dict = Depends(get_current_manager)):
    req = next((r for r in request_list if r["id"] == req_id), None)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req["status"] = data.status
    add_msg(req["user_tg_id"], req_id, data.status, f"Статус заявки #{req_id} змінено на {data.status}")
    return {"message": "Status updated", "request": req}

@app.get("/notifications/{telegram_id}")
def get_msgs(telegram_id: int):
    messages = [m for m in msg_list if m["user_tg_id"] == telegram_id]
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
