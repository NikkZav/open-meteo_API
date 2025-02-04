from .models import CityORM, WeatherORM
from schemas.coordinates import Coordinates
from schemas.city import City
from schemas.weather import Weather
from sqlalchemy import and_
from sqlalchemy.sql import Select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select
from utils.exceptions import CityNotFoundError
from .db import transaction


class CityRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_city_by_id(self, city_id: int) -> City:
        try:
            city_orm = self._get_city_orm(CityORM.id == city_id)
        except CityNotFoundError:
            raise CityNotFoundError(f"City with id {city_id} not found")
        return self._convert_orm_to_city(city_orm)

    def get_city_by_name(self, city_name: str) -> City:
        try:
            city_orm = self._get_city_orm(CityORM.name == city_name)
        except CityNotFoundError:
            raise CityNotFoundError(f"City with name {city_name} not found")
        return self._convert_orm_to_city(city_orm)

    def get_city_by_coord(self, coordinates: Coordinates) -> City:
        try:
            city_orm = self._get_city_orm(
                and_(
                    CityORM.latitude == coordinates.latitude,
                    CityORM.longitude == coordinates.longitude
                )
            )
        except CityNotFoundError:
            raise CityNotFoundError(f"City with coordinates {coordinates}"
                                    f" not found")
        return self._convert_orm_to_city(city_orm)

    def get_cities(self) -> list[City]:
        result = self.db_session.execute(self._get_select_cities_query())
        cities_orm = result.unique().scalars().all()
        return [self._convert_orm_to_city(city_orm) for city_orm in cities_orm]

    def get_city_names(self) -> list[str]:
        result = self.db_session.execute(select(CityORM.name))
        return list(result.scalars())

    def save_city(self, city: City) -> City:
        with transaction(self.db_session):
            city_orm = CityORM(
                name=city.name,
                latitude=city.coordinates.latitude,
                longitude=city.coordinates.longitude,
                weather_records=[WeatherORM(**weather.model_dump())
                                 for weather in (city.weather_records or [])]
            )
            self.db_session.add(city_orm)

        return self._convert_orm_to_city(city_orm)

    def update_weather_records(self, city_id: int,
                               new_weather_records: list[Weather]) -> None:
        """
        Обновляет погодные записи для города с заданным ID.
        Имеющиеся записи обновляются, а тех, которых нет - добавляются.
        """
        city_orm = self._get_city_orm(CityORM.id == city_id)
        existing_records = {record.time: record for record
                            in city_orm.weather_records}
        with transaction(self.db_session):
            for weather in new_weather_records:
                if weather.time in existing_records:
                    self._update_record(weather,
                                        existing_records[weather.time])
                else:
                    self._add_record(weather, city_id)

    def _update_record(self, new_weather: Weather,
                       existing_record: WeatherORM) -> None:
        # Сравниваем только те поля, которые могут изменяться
        updated_data = {key: value for key, value in
                        new_weather.model_dump().items()
                        if getattr(existing_record, key) != value}

        # Если есть изменения, обновляем только изменённые поля
        if updated_data:
            for key, value in updated_data.items():
                setattr(existing_record, key, value)

    def _add_record(self, new_weather: Weather, city_id: int) -> None:
        new_record = WeatherORM(**new_weather.model_dump(),
                                city_id=city_id)
        self.db_session.add(new_record)

    @staticmethod
    def _get_select_cities_query() -> Select[CityORM]:
        """Возвращает базовый запрос для CityORM
        с предзагрузкой weather_records."""
        return select(CityORM).options(joinedload(CityORM.weather_records))

    def _get_city_orm(self, *where_clauses) -> CityORM:
        query = self._get_select_cities_query().where(*where_clauses)
        result = self.db_session.execute(query)
        city_orm = result.scalars().first()
        if city_orm is None:
            raise CityNotFoundError("City not found")
        return city_orm

    def _convert_orm_to_city(self, city_orm: CityORM) -> City:
        """Конвертация CityORM в City с вложенными Weather"""
        weather_records = [
            Weather.model_validate(weather_record, from_attributes=True)
            for weather_record in city_orm.weather_records
        ]
        coordinates = Coordinates(
            latitude=city_orm.latitude,
            longitude=city_orm.longitude
        )
        return City(
            id=city_orm.id,
            name=city_orm.name,
            coordinates=coordinates,
            weather_records=weather_records
        )
