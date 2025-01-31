import sys
from pathlib import Path

# Добавляем путь к текущему каталогу в sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from api import weather, cities
from app.db import create_tables

from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Создаём таблицы при старте приложения
create_tables()

# Запускаем обновление погоды
# loop = asyncio.get_event_loop()

app.include_router(weather.router, prefix="/api")
app.include_router(cities.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
