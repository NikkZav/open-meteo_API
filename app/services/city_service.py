from schemas.coordinates import Coordinates
from repositories.weather_repository import WeatherRepository
from repositories.city_repository import CityRepository
from schemas.city import City, CityParams
from utils.exceptions import (CityNotFoundError,
                              CitySameNameExistsError,
                              CitySameCordsExistsError)
from .update_weather_services import create_periodic_weather_update_task


class CityService:

    def __init__(self,
                 city_repository: CityRepository,
                 weather_repository: WeatherRepository):
        self.city_repo = city_repository
        self.weather_repo = weather_repository

    def get_cities(self,
                   include_weather: bool | None = False) -> list[City | str]:
        """Получение списка городов из БД + (опционально) связанные данные"""
        if include_weather:
            return self.city_repo.get_cities()
        else:
            return self.city_repo.get_city_names()

    def add_city(self, city_params: CityParams) -> City:
        """Добавление города в БД"""
        # Проверка на отсутствие города с таким же именем или координатами
        for getter_city, criteria, error in [
            (self.city_repo.get_city_by_name,  # проверка по имени
             city_params.name, CitySameNameExistsError),
            (self.city_repo.get_city_by_coord,  # проверка по координатам
             city_params.coordinates, CitySameCordsExistsError)
        ]:
            try:  # Пробуем получить город по критериям (название, координаты)
                getter_city(criteria)
            except CityNotFoundError:
                pass  # Если город не найден, то все хорошо, идем дальше
            else:  # Если город найден, то выбрасываем ошибку
                raise error(f"City with '{criteria}' already exists")

        weather_records = self.weather_repo.get_weather_records_by_coord(
            city_params.coordinates)
        city = City(**city_params.model_dump(),
                    weather_records=weather_records)

        new_city = self.city_repo.save_city(city)

        return new_city
