from datetime import date, datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import CityModel
from schemas.city import CitySchema


class CityValidator:
    @staticmethod
    def validate_city_not_exists(city_data: CitySchema, db: Session) -> None:
        existing_city = db.query(CityModel).filter(
            (CityModel.name == city_data.name) |
            (
                (CityModel.latitude == city_data.latitude) &
                (CityModel.longitude == city_data.longitude)
            )
        ).first()
        if existing_city:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Город с таким именем или координатами уже существует"
            )

    @staticmethod
    def validate_city_exists(city_name: str, db: Session) -> CityModel:
        """Проверяет существование города и возвращает его объект."""
        city = db.query(CityModel).filter(CityModel.name == city_name).first()
        if not city:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Город не найден"
            )
        return city  # Возвращаем объект города для дальнейшего использования


class TimeValidator:
    @staticmethod
    def validate_within_current_day(input_time: datetime) -> None:
        if input_time.date() != date.today():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Время должно быть в пределах текущего дня"
            )
