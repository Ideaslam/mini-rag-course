from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from routes import base,data
from pymongo import MongoClient
from helpers.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    uri = settings.MONGODB_URI
    db_name = settings.MONGODB_DATABASE
    client = MongoClient(uri)
    db = client[db_name]
    app.mongo_conn = client
    app.db = db

    yield

    app.mongo_conn.close()
    app.db = None
    app.mongo_conn = None


app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)