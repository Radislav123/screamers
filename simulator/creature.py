import random
from typing import TYPE_CHECKING

from arcade import color

from simulator.tile import Tile
from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.base import Base


class CreatureProjection(WorldObjectProjection):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = color.APRICOT


class Creature(WorldObject):
    projection_class = CreatureProjection
    projections: dict["Tile", projection_class]

    def __init__(self, center_tile: "Tile", bases: list["Base"]) -> None:
        super().__init__(center_tile)
        self.start_base, self.finish_base = random.sample(bases, 2)
        self.scream_radius = 10
