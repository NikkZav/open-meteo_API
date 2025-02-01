import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from api import cities, weather
from db import create_tables

# Добавляем путь к текущему каталогу в sys.path
sys.path.append(str(Path(__file__).resolve().parent))


app = FastAPI()

# Создаём таблицы при старте приложения
create_tables()

app.include_router(weather.router, prefix="/api")
app.include_router(cities.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
