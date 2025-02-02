from .models import CityORM
from schemas.coordinates import Coordinates
from schemas.city import City
from schemas.weather import Weather
from sqlalchemy import and_
from sqlalchemy.orm import Session
from utils.exceptions import CityNotFoundError


class CityRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_weather_records_in_city(self, city_name: str) -> list[Weather]:
        """
        Возвращает прогноз погоды для города по его названию.
        Сам прогноз берётся из БД
        """
        return self.get_city_by_name(city_name).weather_records

    def get_city_by_id(self, city_id: int) -> City:
        city_orm = self.db_session.query(CityORM).filter(
            CityORM.id == city_id
        ).first()
        if city_orm is None:
            raise CityNotFoundError(f"City by ID {city_id} not found")
        return self._convert_orm_to_city(city_orm) if city_orm else None

    def get_city_by_name(self, city_name: str) -> City:
        city_orm = self.db_session.query(CityORM).filter(
            CityORM.name == city_name
        ).first()
        if city_orm is None:
            raise CityNotFoundError(f"City {city_name} not found")
        return self._convert_orm_to_city(city_orm)

    def get_city_by_coodrinates(self, coordinates: Coordinates) -> City:
        city_orm = self.db_session.query(CityORM).filter(and_(
            CityORM.latitude == coordinates.latitude,
            CityORM.longitude == coordinates.longitude
        )).first()
        if city_orm is None:
            raise CityNotFoundError(
                f"City by coordinates {Coordinates} not found")
        return self._convert_orm_to_city(city_orm) if city_orm else None

    def get_cities(self) -> list[City]:
        return [self._convert_orm_to_city(city_orm) for city_orm in
                self.db_session.query(CityORM).all()]

    def _convert_orm_to_city(self, city: CityORM) -> City:
        """Конвертация CityORM в City с вложенными Weather"""
        weather_records = [
            Weather.model_validate(record.__dict__)
            for record in city.weather_records
        ]
        coordinates = Coordinates(
            latitude=city.latitude,
            longitude=city.longitude
        )
        return City(
            id=city.id,
            name=city.name,
            coordinates=coordinates,
            weather_records=weather_records
        )
