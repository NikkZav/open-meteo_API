from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class WeatherORM(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    time = Column(DateTime, nullable=False)
    temperature_2m = Column(Float, nullable=True)
    wind_speed_10m = Column(Float, nullable=True)
    pressure_msl = Column(Float, nullable=True)
    rain = Column(Float, nullable=True)
    relative_humidity_2m = Column(Float, nullable=True)

    city = relationship("CityORM", back_populates="weather_records")


class CityORM(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather_records = relationship("WeatherORM", back_populates="city")
