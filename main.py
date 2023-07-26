
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail
from aio_pika import connect, Message
from sql_app import crud, models, schemas
from sql_app.database import engine, SessionLocal
from util.email_body import EmailSchema

from prometheus_fastapi_instrumentator import Instrumentator
import json

conf = ConnectionConfig(
    MAIL_USERNAME="7719b05f8446ce",
    MAIL_PASSWORD="fed80d43d14b76",
    MAIL_FROM="pedro.amancio1@estudante.ufla.br",
    MAIL_PORT=587,
    MAIL_SERVER="sandbox.smtp.mailtrap.io",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Patter Singleton
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return HTMLResponse(content = "POST /AddTasks<br />GET /GetStats")

@app.post("/dtm-lote")
async def dtm_lote(info: Request, db: Session = Depends(get_db)):
    info = await info.json()
    print(info)
    dtms = info.get("dtms", [])
    for dtm in dtms:
        print("enviando [*] ", json.dumps(dtm))
        await send_rabbitmq(dtm)


async def send_rabbitmq(msg = {}):
    connection = await connect("amqp://guest:guest@rabbitmq:5672/")

    channel = await connection.channel()

    await channel.default_exchange.publish(
        Message(json.dumps(msg).encode("utf-8")),
        routing_key = "dtm_queue"
    )

    await connection.close()
