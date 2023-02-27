from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

messages = []
@app.get("/message")
async def message():
    return {"messages": messages}


class Message(BaseModel):
    author: str
    message: str


@app.post("/send-message")
async def send_message(msg: Message):
    print(msg.message)
    messages.append(msg.message)
    return "OK"


#uvicorn api_server:app --reload
#pip insall uvicorn
