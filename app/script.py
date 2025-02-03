import uvicorn
from fastapi import FastAPI

from routing import cities, weather
from repositories.db import create_tables


app = FastAPI()

# Создаём таблицы при старте приложения
create_tables()

app.include_router(weather.router, prefix="/api")
app.include_router(cities.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
