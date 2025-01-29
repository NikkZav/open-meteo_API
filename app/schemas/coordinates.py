from pydantic import BaseModel, Field


class CoordinatesSchema(BaseModel):
    latitude: float = Field(
        ge=-90, le=90,
        description="Диапазон значений координат широты от -90 до 90"
    )
    longitude: float = Field(
        ge=-180, le=180,
        description="Диапазон значений координат долготы от -180 до 180"
    )
