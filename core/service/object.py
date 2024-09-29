from typing import Self

from core.service import settings
from core.service.logger import Logger


class Object:
    settings = settings.Settings()

    def __new__(cls, *args, **kwargs) -> "Self":
        instance = super().__new__(cls, *args, **kwargs)
        instance.logger = Logger(cls.__name__)
        return instance
