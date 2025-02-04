from .log import logger


class OpenMeteoAPIError(Exception):
    """Общий класс ошибок для API open-meteo."""
    def __init__(self, message="Open-Meteo API error"):
        super().__init__(message)
        logger.error(message)


class CityNotFoundError(Exception):
    """Ошибка, возникающая, когда город не найден."""
    def __init__(self, message="City not found"):
        super().__init__(message)
        logger.error(message)


class WeatherInCityNotFoundError(Exception):
    """Ошибка, возникающая, когда не найдена
    ни одна погодная запись для города."""
    def __init__(self, message="Weather in city not found"):
        super().__init__(message)
        logger.error(message)


class TimeRangeError(Exception):
    """Ошибка, возникающая, когда диапазон времени некорректен."""
    def __init__(self, message="Time range error"):
        super().__init__(message)
        logger.error(message)


class SameCityExistsError(Exception):
    """Ошибка, означающая дублирование города (по тем или иным критейриям)."""
    def __init__(self, message="Same city exists error"):
        super().__init__(message)
        logger.error(message)


class CitySameNameExistsError(SameCityExistsError):
    """Ошибка, возникающая, при попытке создать город с названием,
    которое однозначно идентифицирует другой город"""
    def __init__(self, message="City with same name exists error"):
        super().__init__(message)
        logger.error(message)


class CitySameCordsExistsError(SameCityExistsError):
    """Ошибка, возникающая, при попытке создать город с координатами,
    которые однозначно идентифицируют другой город."""
    def __init__(self, message="City with same cordiantes exists error"):
        super().__init__(message)
        logger.error(message)
