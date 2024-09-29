from arcade import Sprite
from pyglet.math import Vec2

from core.service.object import Object


class BaseSprite(Sprite, Object):
    pass


class Base(Object):
    counter = 0

    def __init__(self, position: Vec2) -> None:
        self.position = position

        self.id = self.counter
        self.__class__.counter += 1

        self.sprite = BaseSprite()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def on_update(self) -> None:
        pass
