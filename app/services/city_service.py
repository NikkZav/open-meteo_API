from sqlalchemy.orm import Session, joinedload
from models import CityModel, WeatherModel
from schemas.city import CitySchema
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema
from services.weather_service import get_weather_in_city
from datetime import datetime


def get_city_or_none(recognizer: str | int, db: Session) -> CityModel | None:
    condition = (CityModel.name == recognizer) \
        if isinstance(recognizer, str) else (CityModel.id == recognizer)
    return db.query(CityModel).filter(condition).first()


class CityService:
    def __init__(self, db: Session, city: CitySchema | CityModel = None):
        self.db = db
        if isinstance(city, CityModel):
            self.city = city
        elif isinstance(city, CitySchema):
            self.city_data = city

    def check_city_existence(self) -> bool:
        return get_city_or_none(self.city_data.name, self.db) is not None

    def refresh_weather_records_for_city(self) -> None:
        """
        Обновляет записи о погоде для указанного города
        или инициализирует их, если данные отсутствуют.

        Получает актуальный прогноз погоды и синхронизирует его с базой данных,
        добавляя новые записи или обновляя существующие.
        """
        weather_records: list[WeatherSchema] = get_weather_in_city(self.city)

        # Создаём словарь с существующими записями по времени
        existing_records = {
            record.time: record for record in self.city.weather_records
        }

        for weather in weather_records:
            if weather.time in existing_records:
                # Обновляем существующую запись
                existing_record = existing_records[weather.time]
                for key, value in weather.model_dump().items():
                    setattr(existing_record, key, value)
            else:
                # Добавляем новую запись (если нужно)
                new_weather = WeatherModel(
                    city_id=self.city.id,
                    **weather.model_dump()
                )
                self.db.add(new_weather)

    def add_city(self) -> CityModel:
        """Добавление города и начального прогноза."""
        self.city = CityModel(
            name=self.city_data.name,
            latitude=self.city_data.latitude,
            longitude=self.city_data.longitude
        )
        try:
            self.db.add(self.city)
            self.db.flush()  # Фиксируем id города перед добавлением погоды
            self.refresh_weather_records_for_city()  # Добавляем погоду
            self.db.commit()
            self.db.refresh(self.city)
        except Exception as e:
            self.db.rollback()
            raise e

        return self.city

    def get_cities(self, all_statistic_with_weather: bool = False
                   ) -> list[str | dict]:
        if all_statistic_with_weather:
            # В ТЗ просят выводить только список городов
            # но я добавил возможность получить всю информацию, включая погоду
            cities = self.db.query(CityModel).options(
                joinedload(CityModel.weather_records)
            ).all()
            return cities
        else:
            return [city.name for city in
                    self.db.query(CityModel).all()]
