import os

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import json
from datetime import datetime, timedelta

SECRET_KEY = "fdjhfhdjhfdjhfds45fds1f2ds1fdsfdsbfhdsb"

FILENAME = "./db.json"

app = FastAPI()

messages = []
users = []


if os.path.exists(FILENAME):
    with open(FILENAME, "r") as f:
        data = json.load(f)
        users = data["users"]
        messages = data["messages"]


def save_db():
    with open(FILENAME, "w") as f:
        data = {
            "users": users,
            "messages": messages
        }
        json.dump(data, f, indent=True)


@app.get("/message")
async def message(token: str = Header(None)):
    try:
        if token == "":
            return {"message": "Brak tokena"}
        jwt.decode(token, key=SECRET_KEY, algorithms="HS256")
        return {"messages": messages}

    except jwt.exceptions.InvalidSignatureError:
        return {"message": "Niepoprawne dane"}
    except jwt.exceptions.ExpiredSignatureError:
        return {"message": "Token wygasl"}


class Message(BaseModel):
    author: str
    message: str


@app.post("/send-message")
async def send_message(msg: Message, token: str = Header(None)):
    try:
        if token == "":
            return {"message": "Brak tokena"}
        token_data = jwt.decode(token, key=SECRET_KEY, algorithms="HS256")
        print(token_data)
        messages.append(token_data["username"] + ": " + msg.message)
        save_db()
        return {"message": "OK"}
    except jwt.exceptions.InvalidSignatureError:
        return {"message": "Niepoprawne dane"}
    except jwt.exceptions.ExpiredSignatureError:
        return {"message": "Token wygasl"}


class User(BaseModel):
    username: str
    password: str


def is_correct_username_and_password(username, password):
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False


def username_exist(username):
    for user in users:
        if user["username"] == username:
            return True
    return False


@app.post("/login")
async def login(user: User):
    if is_correct_username_and_password(user.username, user.password):
        token = jwt.encode({
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(minutes=60)
        }, SECRET_KEY, algorithm="HS256")
        return {"message": "zalogowano", "token": token}
    else:
        return {"message": "niepoprawne dane logowania"}


@app.post("/register")
async def register(user: User):
    if username_exist(user.username):
        return JSONResponse(status_code=400, content={"message": "podana nazwa uzytkownika juz istnieje"})
    users.append({"username": user.username, "password": user.password})
    save_db()
    return JSONResponse(status_code=200, content={"message": "OK"})


# uruchomienie
# uvicorn api_server:app --reload

# instalacja:
# pip insall uvicorn

# zapisuje wersje bibliotek do pliku
# pip freeze > requirements.txt

