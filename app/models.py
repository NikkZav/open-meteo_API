from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base
from json import loads


class WeatherModel(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    time = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    pressure_msl = Column(Float, nullable=True)
    rain = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    
    city = relationship("CityModel", back_populates="weather_records")


class CityModel(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather_records = relationship("WeatherModel", back_populates="city")
    # weather = Column(JSON, nullable=True)  # JSON-поле для хранения погоды

    # @property
    # def parsed_weather(self):
    #     return loads(self.weather) if self.weather else None
