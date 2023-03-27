import requests
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import threading
import time
from database import Database


SECRET_KEY = "fdjhfhdjhfdjhfds45fds1f2ds1fdsfdsbfhdsb"

app = FastAPI()
db = Database()


@app.get("/message")
async def message(token: str = Header(None)):
    try:
        if token == "":
            return {"message": "Brak tokena"}
        token_data = jwt.decode(token, key=SECRET_KEY, algorithms="HS256")
        if not db.username_exist(token_data["username"]):
            return {"message": "Uzytkownik zostal skasowany"}

        return {"messages": db.get_all_message()}

    except jwt.exceptions.InvalidSignatureError:
        return {"message": "Niepoprawne dane"}
    except jwt.exceptions.ExpiredSignatureError:
        return {"message": "Token wygasl"}


class Message(BaseModel):
    message: str


@app.post("/send-message")
async def send_message(msg: Message, token: str = Header(None)):
    try:
        if token == "":
            return {"message": "Brak tokena"}
        token_data = jwt.decode(token, key=SECRET_KEY, algorithms="HS256")
        if not db.username_exist(token_data["username"]):
            return {"message": "Uzytkownik zostal skasowany"}

        print(token_data)
        db.add_message(msg.message, token_data["username"])
        print(msg.message)
        if msg.message.startswith("set-notification"):
            command, date, product, *other = msg.message.split(" ")
            db.add_notification(token_data["username"], product, date)
        elif msg.message == "delete-account":
            db.delete_user(token_data["username"])

        return {"message": "OK"}
    except jwt.exceptions.InvalidSignatureError:
        return {"message": "Niepoprawne dane"}
    except jwt.exceptions.ExpiredSignatureError:
        return {"message": "Token wygasl"}


class User(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(user: User):
    if db.is_correct_username_and_password(user.username, user.password):
        token = jwt.encode({
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(minutes=60)
        }, SECRET_KEY, algorithm="HS256")
        return {"message": "zalogowano", "token": token}
    else:
        return {"message": "niepoprawne dane logowania"}


@app.post("/register")
async def register(user: User):
    if db.username_exist(user.username):
        return JSONResponse(status_code=400, content={"message": "podana nazwa uzytkownika juz istnieje"})
    db.add_user(user.username, user.password)
    return JSONResponse(status_code=200, content={"message": "OK"})


# uruchomienie
# uvicorn api_server:app --reload --host="0.0.0.0"

# instalacja:
# pip insall uvicorn

# zapisuje wersje bibliotek do pliku
# pip freeze > requirements.txt

def send_api_call(message):
    url = "https://maker.ifttt.com/trigger/data_wybila/json/with/key/c_gqYRvJ5NVJxyD-PR4fpP"
    body = {"message": message}
    response = requests.post(url, json=body)
    print(response)
    return response.ok


def check_notifications():
    print(datetime.now(), "Sprawdzam powiadomienia ---------------------------------")
    for notif in db.get_current_notifications():
        date = datetime.strptime(notif["date"], "%Y-%m-%d")
        if date.date() == datetime.now().date():
            if send_api_call(notif):
                db.delete_notification(notif["id"])


def do_in_loop():
    print("Loop started!")
    while True:
        check_notifications()
        time.sleep(10)


thread = threading.Thread(target=do_in_loop)
thread.start()
