from typing import Self

from pyglet.math import Vec2

from core.service import settings
from core.service.logger import Logger


class Object:
    settings = settings.Settings()
    counter = 0

    def __new__(cls, *args, **kwargs) -> "Self":
        instance = super().__new__(cls)
        instance.logger = Logger(cls.__name__)
        return instance

    def __init__(self) -> None:
        self.id = self.counter
        self.__class__.counter += 1

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def on_update(self) -> None:
        pass


class PhysicalObject(Object):
    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__()
        self.position_x = position_x
        self.position_y = position_y
        self.position = Vec2(self.position_x, self.position_y)
