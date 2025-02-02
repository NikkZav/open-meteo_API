from repositories.weather_repository import WeatherRepository
from repositories.city_repository import CityRepository


class CityService:

    def __init__(self,
                 city_repository: CityRepository,
                 weather_repository: WeatherRepository):
        self.city_repos = city_repository
        self.weather_repos = weather_repository
