import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from routing import cities, weather
from repositories.db import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц перед запуском сервера
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(weather.router, prefix="/api")
app.include_router(cities.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
