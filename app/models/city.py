from sqlalchemy import Column, Integer, String, Float, JSON
from core.db import Base
from json import loads

# class WeatherFieldsMixin():
#     temperature = Column(Float, nullable=True)
#     wind_speed = Column(Float, nullable=True)
#     pressure_msl = Column(Float, nullable=True)
#     rain = Column(Float, nullable=True)
#     humidity = Column(Float, nullable=True)


# class CityModel(WeatherFieldsMixin, Base):
#     __tablename__ = "cities"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, index=True)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)

class CityModel(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather = Column(JSON, nullable=True)  # JSON-поле для хранения погоды

    @property
    def parsed_weather(self):
        return loads(self.weather) if self.weather else None
