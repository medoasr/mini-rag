from fastapi import FastAPI
from routes import data,base
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings


app=FastAPI()

@app.on_event('startup')
async  def startdb_client():
    settings=get_settings()
    app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client=app.mongo_conn[settings.MONGODB_DATABASE]
@app.on_event('shutdown')
async  def shutdown_db():
    app.mongo_conn.close()


app.include_router(base.base_router)
app.include_router(data.data_router)

