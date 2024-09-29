from arcade import Sprite
from pyglet.math import Vec2

from core.service.object import Object


class CreatureSprite(Sprite, Object):
    pass


class Creature(Object):
    scream_radius = 10
    counter = 0

    def __init__(self, position: Vec2) -> None:
        self.position = position

        self.id = self.counter
        self.__class__.counter += 1

        self.sprite = CreatureSprite()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def on_update(self) -> None:
        pass
