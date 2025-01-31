from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class WeatherModel(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    time = Column(DateTime, nullable=False)
    temperature_2m = Column(Float, nullable=True)
    wind_speed_10m = Column(Float, nullable=True)
    pressure_msl = Column(Float, nullable=True)
    rain = Column(Float, nullable=True)
    relative_humidity_2m = Column(Float, nullable=True)

    city = relationship("CityModel", back_populates="weather_records")


class CityModel(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather_records = relationship("WeatherModel", back_populates="city")

