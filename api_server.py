import requests
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import threading
import time
import sqlite3

conn = sqlite3.connect("baza.db", check_same_thread=False)


def add_user(username, password, admin=False):
    conn.execute(f"INSERT INTO Users(Username, Password, Admin) VALUES('{username}', '{password}', {admin});")
    conn.commit()


def add_message(text, author):
    conn.execute(f"INSERT INTO Messages(Text, Author) VALUES('{text}', '{author}');")
    conn.commit()


def delete_user(username):
    conn.execute(f"DELETE FROM Users WHERE username = '{username}';")
    conn.commit()


def add_notification(author, product, date):
    conn.execute(f"INSERT INTO Notifications(Author, Product, Expiration) VALUES('{author}', '{product}', '{date}');")
    conn.commit()


def get_all_message():
    cursor = conn.execute("SELECT Author || ': ' || Text as Msg FROM Messages;")
    messages = []
    for row in cursor:
        messages.append(row[0])
    return messages


def get_current_notifications():
    cursor = conn.execute("SELECT * FROM Notifications WHERE Expiration <= DATE('now');")
    messages = []
    for row in cursor:
        messages.append({
            "id": row[0],
            "author": row[1],
            "product": row[2],
            "date": row[3]
        })
    return messages


def delete_notification(_id):
    conn.execute(f"DELETE FROM Notifications WHERE ID = {_id};")
    conn.commit()


try:
    conn.execute("""CREATE TABLE IF NOT EXISTS Users
    (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username NVARCHAR(30) UNIQUE,
        Password NVARCHAR(30),
        Admin BOOL DEFAULT FALSE
    );""")

    conn.execute("""CREATE TABLE IF NOT EXISTS Messages
    (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Text NVARCHAR(100),
        Author NVARCHAR(30)
    );""")

    conn.execute("""CREATE TABLE IF NOT EXISTS Notifications
    (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Author NVARCHAR(30),
        Product NVARCHAR(30),
        Expiration DATE
    )
    """)

    add_user("mielony", "cos12", True)
except:
    print("Jakis blad DB, prawdopodobnie Admin juz istnieje")


SECRET_KEY = "fdjhfhdjhfdjhfds45fds1f2ds1fdsfdsbfhdsb"

app = FastAPI()


@app.get("/message")
async def message(token: str = Header(None)):
    try:
        if token == "":
            return {"message": "Brak tokena"}
        token_data = jwt.decode(token, key=SECRET_KEY, algorithms="HS256")
        if not username_exist(token_data["username"]):
            return {"message": "Uzytkownik zostal skasowany"}

        return {"messages": get_all_message()}

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
        if not username_exist(token_data["username"]):
            return {"message": "Uzytkownik zostal skasowany"}

        print(token_data)
        add_message(msg.message, token_data["username"])
        print(msg.message)
        if msg.message.startswith("set-notification"):
            command, date, product, *other = msg.message.split(" ")
            add_notification(token_data["username"], product, date)
        elif msg.message == "delete-account":
            delete_user(token_data["username"])

        return {"message": "OK"}
    except jwt.exceptions.InvalidSignatureError:
        return {"message": "Niepoprawne dane"}
    except jwt.exceptions.ExpiredSignatureError:
        return {"message": "Token wygasl"}


class User(BaseModel):
    username: str
    password: str


def is_correct_username_and_password(username, password):
    cursor = conn.execute(f"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{password}'")
    for row in cursor:
        return True
    return False


def username_exist(username):
    cursor = conn.execute(f"SELECT * FROM Users WHERE Username = '{username}'")
    for row in cursor:
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
    add_user(user.username, user.password)
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
    for notif in get_current_notifications():
        date = datetime.strptime(notif["date"], "%Y-%m-%d")
        if date.date() == datetime.now().date():
            if send_api_call(notif):
                delete_notification(notif["id"])


def do_in_loop():
    print("Loop started!")
    while True:
        check_notifications()
        time.sleep(10)


thread = threading.Thread(target=do_in_loop)
thread.start()
