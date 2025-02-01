from sqlalchemy.orm import Session, joinedload
from models import CityModel, WeatherModel
from schemas.city import CitySchema, CityResponse
from schemas.weather import WeatherSchema, WeatherResponse
from services.weather_service import get_weather_records_in_city
from services.common_utils import get_city_or_none


class CityService:
    """Сервис для работы с городами."""
    def __init__(self, db: Session, city: CitySchema | CityModel = None):
        self.db = db
        if isinstance(city, CityModel):
            self.city = city
        elif isinstance(city, CitySchema):
            self.city_data = city

    def check_city_existence(self) -> bool:
        return get_city_or_none(self.city_data.name, self.db) is not None
    
    def _update_existing_weather_record(self, existing_record,
                                        weather: WeatherSchema):
        """Обновляет существующую запись о погоде."""
        for key, value in weather.model_dump().items():
            setattr(existing_record, key, value)

    def _add_new_weather_record(self, weather: WeatherSchema):
        """Добавляет новую запись о погоде."""
        new_weather = WeatherModel(
            city_id=self.city.id,
            **weather.model_dump()
        )
        self.db.add(new_weather)

    def refresh_weather_records_for_city(self) -> None:
        """
        Обновляет записи о погоде для указанного города
        или инициализирует их, если данные отсутствуют.

        Получает актуальный прогноз погоды и синхронизирует его с базой данных,
        добавляя новые записи или обновляя существующие.
        """
        weather_records: list[WeatherSchema] = \
            get_weather_records_in_city(self.city)
        # Создаём словарь с существующими записями по времени
        existing_records = {record.time: record for record
                            in self.city.weather_records}

        for weather in weather_records:
            if weather.time in existing_records:
                # Обновляем существующую запись
                self._update_existing_weather_record(
                    existing_records[weather.time], weather)
            else:
                # Добавляем новую запись (если нужно)
                self._add_new_weather_record(weather)

    def add_city(self) -> CityModel:
        """Добавление города в БД и обновление погоды для него"""
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

    def _convert_city_to_response(self, city: CityModel) -> CityResponse:
        """Конвертация CityModel в CityResponse с вложенными WeatherResponse"""
        weather_records = [
            WeatherResponse.model_validate(record)
            for record in city.weather_records
        ]
        return CityResponse(
            id=city.id,
            name=city.name,
            latitude=city.latitude,
            longitude=city.longitude,
            weather_records=weather_records
        )

    def get_cities(self, include_weather: bool = False) -> list[CityResponse | str]:
        """Получение списка городов из БД + (опционально) связанные данные"""
        if include_weather:
            cities = self.db.query(CityModel).options(
                joinedload(CityModel.weather_records)
            ).all()
            return [self._convert_city_to_response(city) for city in cities]
        else:
            return [city.name for city in self.db.query(CityModel).all()]
