class OpenMeteoAPIError(Exception):
    """Общий класс ошибок для API open-meteo."""


class CityNotFoundError(Exception):
    """Ошибка, возникающая, когда город не найден."""


class WeatherInCityNotFoundError(Exception):
    """Ошибка, возникающая, когда не найдена
    ни одна погодная запись для города."""


class TimeRangeError(Exception):
    """Ошибка, возникающая, когда диапазон времени некорректен."""


class SameCityExistsError(Exception):
    """Ошибка, означающая дублирование города (по тем или иным критейриям)."""


class CitySameNameExistsError(SameCityExistsError):
    """Ошибка, возникающая, при попытке создать город с названием,
    которое однозначно идентифицирует другой город"""


class CitySameCordsExistsError(SameCityExistsError):
    """Ошибка, возникающая, при попытке создать город с координатами,
    которые однозначно идентифицируют другой город."""
