import math
from typing import TYPE_CHECKING

import arcade
from arcade.shape_list import Shape

from core.service.object import PhysicalObject, ProjectionObject


if TYPE_CHECKING:
    from simulator.base import Base
    from simulator.creature import Creature


class TileProjection(ProjectionObject):
    border_color: tuple[int, int, int, int]
    overlap_distance: float
    border_width: float
    radius: float
    width: float
    height: float
    position_x: float
    position_y: float
    width_offset: float
    height_offset: float
    border_points: tuple[tuple[float, float], ...]
    border: Shape

    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__()
        self.tile_position_x = position_x
        self.tile_position_y = position_y

    def init(self, map_offset_x: int, map_offset_y: int, map_coeff: int) -> None:
        sqrt = math.sqrt(3)
        self.border_color = (100, 100, 100, 255)

        self.overlap_distance = 0 * map_coeff
        self.border_width = 1
        self.radius = map_coeff / 2
        self.width = sqrt * self.radius + self.overlap_distance
        self.height = 2 * self.radius + self.overlap_distance
        self.position_x = (sqrt * self.tile_position_x + sqrt / 2 * self.tile_position_y) * self.radius + map_offset_x
        self.position_y = (3 / 2 * self.tile_position_y) * self.radius + map_offset_y

        width_offset = self.width / 2
        height_offset = self.height / 2
        self.border_points = (
            (self.position_x - width_offset, self.position_y - height_offset / 2),
            (self.position_x - width_offset, self.position_y + height_offset / 2),
            (self.position_x, self.position_y + height_offset),
            (self.position_x + width_offset, self.position_y + height_offset / 2),
            (self.position_x + width_offset, self.position_y - height_offset / 2),
            (self.position_x, self.position_y - height_offset)
        )

        self.border = arcade.shape_list.create_line_loop(
            self.border_points,
            self.border_color,
            self.border_width
        )

        self.inited = True


class Tile(PhysicalObject):
    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__(position_x, position_y)
        self.projection = TileProjection(position_x, position_y)

        self.object: Creature | Base | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.position_x, self.position_y}"
