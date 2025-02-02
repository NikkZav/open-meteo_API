from sqlalchemy import and_
from sqlalchemy.orm import Session

from models import CityModel
from schemas.coordinates import CoordinatesSchema


def get_city_or_none(city_identifier: str | int | CoordinatesSchema,
                     db: Session) -> CityModel | None:
    if isinstance(city_identifier, CoordinatesSchema):
        condition = and_(
            CityModel.latitude == city_identifier.latitude,
            CityModel.longitude == city_identifier.longitude
        )
    elif isinstance(city_identifier, str):
        condition = CityModel.name == city_identifier
    elif isinstance(city_identifier, int):
        condition = CityModel.id == city_identifier
    else:
        return None
    return db.query(CityModel).filter(condition).first()
