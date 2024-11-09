from typing import Any, Self

from arcade.shape_list import Shape
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id = self.counter
        self.__class__.counter += 1

    def init(self, *args, **kwargs) -> Any:
        pass

    def start(self, *args, **kwargs) -> Any:
        pass

    def stop(self, *args, **kwargs) -> Any:
        pass


class ProjectionObject(Object):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.inited = False
        self.shape: Shape | None = None

    def on_draw(self, *args, **kwargs) -> Any:
        pass


class PhysicalObject(Object):
    def __init__(self, x: int, y: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.position = Vec2(self.x, self.y)

    def on_update(self, *args, **kwargs) -> Any:
        pass
