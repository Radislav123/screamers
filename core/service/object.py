from typing import Any, Self

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

    def init(self, *args, **kwargs) -> Any:
        pass

    def start(self, *args, **kwargs) -> Any:
        pass

    def stop(self, *args, **kwargs) -> Any:
        pass


class PhysicalObject(Object):
    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__()
        self.position_x = position_x
        self.position_y = position_y
        self.position = Vec2(self.position_x, self.position_y)

    def on_update(self, *args, **kwargs) -> Any:
        pass


class ProjectionObject(Object):
    def __init__(self) -> None:
        super().__init__()
        self.inited = False

    def on_draw(self, *args, **kwargs) -> Any:
        pass
