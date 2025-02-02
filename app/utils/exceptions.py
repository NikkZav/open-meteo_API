class OpenMeteoAPIError(Exception):
    """Общий класс ошибок для API open-meteo."""


class CityNotFoundError(Exception):
    """Ошибка, возникающая, когда город не найден."""


class TimeRangeError(Exception):
    """Ошибка, возникающая, когда диапазон времени некорректен."""
