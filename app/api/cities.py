from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.city_service import CityService
from schemas.city import CitySchema
from core.db import SessionLocal
from http import HTTPStatus

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add_city")
def add_city_endpoint(city_data: CitySchema,
                      db: Session = Depends(get_db)):
    city_service = CityService(city_data, db)
    # Проверяем существование города
    if city_service.check_city_existence():
        raise HTTPException(status_code=HTTPStatus.CONFLICT,
                            detail="Этот город уже добавлен")
    # Добавляем новый город в БД
    new_city = city_service.add_city()
    return {"message": "Город успешно добавлен",
            "id": new_city.id,
            "name": new_city.name}


@router.get("/cities")
def get_cities(with_weather: bool | None = None,
               db: Session = Depends(get_db)):
    city_service = CityService(None, db)
    return city_service.get_cities(with_weather=with_weather)
