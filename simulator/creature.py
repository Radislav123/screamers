import random
from typing import TYPE_CHECKING

from arcade import color

from simulator.world_object import WorldObject, WorldObjectSprite


if TYPE_CHECKING:
    from simulator.base import Base


class CreatureSprite(WorldObjectSprite):
    color = color.APRICOT


class Creature(WorldObject):
    sprite_class = CreatureSprite

    def __init__(self, position_x: int, position_y: int, bases: list["Base"]) -> None:
        super().__init__(position_x, position_y)
        self.start_base, self.finish_base = random.sample(bases, 2)
        self.scream_radius = 10
