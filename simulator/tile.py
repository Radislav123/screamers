import math
from typing import TYPE_CHECKING

import arcade
from arcade import color
from arcade.shape_list import Shape

from core.service.object import PhysicalObject, ProjectionObject


if TYPE_CHECKING:
    from simulator.base import Base
    from simulator.creature import Creature
    from simulator.world import Map, Tiles, WorldBorder, WorldBorders


class TileProjection(ProjectionObject):
    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__()
        self.tile_x = position_x
        self.tile_y = position_y
        self.border_color = color.DIM_GRAY
        self.border_thickness = 1
        self.selected_border_thickness = 3
        self.selected = False

        self.overlap_distance: float | None = None
        self.radius: float | None = None
        self.width: float | None = None
        self.height: float | None = None
        self.x: float | None = None
        self.y: float | None = None
        self.width_offset: float | None = None
        self.height_offset: float | None = None
        self.border_points: tuple[tuple[float, float], ...] | None = None
        self.shape: Shape | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.tile_x, self.tile_y}"

    def init(self, offset_x: float, offset_y: float, coeff: float, tilt_coeff: float) -> None:
        sqrt = math.sqrt(3)

        self.overlap_distance = 0 * coeff
        self.radius = coeff / 2
        self.width = sqrt * self.radius + self.overlap_distance
        self.height = (2 * self.radius + self.overlap_distance) * tilt_coeff
        self.x = (sqrt * self.tile_x + sqrt / 2 * self.tile_y) * self.radius + offset_x
        self.y = (3 / 2 * self.tile_y) * self.radius * tilt_coeff + offset_y

        width_offset = self.width / 2
        height_offset = self.height / 2
        self.border_points = (
            (self.x - width_offset, self.y - height_offset / 2),
            (self.x - width_offset, self.y + height_offset / 2),
            (self.x, self.y + height_offset),
            (self.x + width_offset, self.y + height_offset / 2),
            (self.x + width_offset, self.y - height_offset / 2),
            (self.x, self.y - height_offset)
        )

        self.shape = arcade.shape_list.create_line_loop(
            self.border_points,
            self.border_color,
            self.selected_border_thickness if self.selected else self.border_thickness
        )

        self.inited = True

    def select(self, world_map: "Map") -> None:
        world_map.selected_tile = self
        self.inited = False
        self.selected = True

    def deselect(self, world_map: "Map") -> None:
        world_map.selected_tile = None
        self.inited = False
        self.selected = False

    def on_click(self, world_map: "Map") -> None:
        if self.selected:
            self.deselect(world_map)
        else:
            self.select(world_map)


class Tile(PhysicalObject):
    neighbour_offsets = ((0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1))
    neighbours: list["Tile"]

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.projection = TileProjection(x, y)

        self.object: Creature | Base | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.x, self.y}"

    def init(self, border_bounds: "WorldBorder", world_borders: "WorldBorders", all_tiles: "Tiles") -> None:
        self.neighbours = []
        for offset_x, offset_y in self.neighbour_offsets:
            x = self.x + offset_x
            y = self.y + offset_y

            if x > border_bounds.x_upper:
                x = border_bounds.x_lower
            if x < border_bounds.x_lower:
                x = border_bounds.x_upper
            if y > border_bounds.y_upper:
                y = border_bounds.y_lower
            if y < border_bounds.y_lower:
                y = border_bounds.y_upper
            world_border = world_borders[x][y]

            if x > world_border.x_upper:
                x = world_border.x_upper
            if x < world_border.x_lower:
                x = world_border.x_lower
            if y > world_border.y_upper:
                y = world_border.y_upper
            if y < world_border.y_lower:
                y = world_border.y_lower
            self.neighbours.append(all_tiles[x][y])
