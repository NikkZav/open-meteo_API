from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import CityModel
from schemas.coordinates import CoordinatesSchema


def get_city_or_none(recognizer: str | int | CoordinatesSchema,
                     db: Session) -> CityModel | None:
    if isinstance(recognizer, CoordinatesSchema):
        condition = and_(
            CityModel.latitude == recognizer.latitude,
            CityModel.longitude == recognizer.longitude
        )
    elif isinstance(recognizer, str):
        condition = CityModel.name == recognizer
    elif isinstance(recognizer, int):
        condition = CityModel.id == recognizer
    else:
        return None
    return db.query(CityModel).filter(condition).first()
