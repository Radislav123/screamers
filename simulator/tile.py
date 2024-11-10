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
        world_map.selected_tiles.add(self)
        self.inited = False
        self.selected = True

    def deselect(self, world_map: "Map") -> None:
        world_map.selected_tiles.remove(self)
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

    # https://www.redblobgames.com/grids/hexagons/#wraparound
    def init(
            self,
            border_bounds: "WorldBorder",
            world_borders: "WorldBorders",
            all_tiles: "Tiles",
            world_radius: int
    ) -> None:
        self.neighbours = []

        for direction, (offset_x, offset_y) in enumerate(self.neighbour_offsets):
            x = self.x + offset_x
            y = self.y + offset_y

            border_x = x
            border_y = y
            if border_x > border_bounds.x_upper:
                border_x = border_bounds.x_lower
            if border_x < border_bounds.x_lower:
                border_x = border_bounds.x_upper
            if border_y > border_bounds.y_upper:
                border_y = border_bounds.y_lower
            if border_y < border_bounds.y_lower:
                border_y = border_bounds.y_upper
            neighbour_border = world_borders[border_x][border_y]

            mirrors = (
                (world_radius, -world_radius * 2),
                (-world_radius, -world_radius),
                (-world_radius * 2, world_radius),
                (-world_radius, world_radius * 2),
                (world_radius, world_radius),
                (world_radius * 2, -world_radius)
            )

            self_border = world_borders[self.x][self.y]
            corners = (
                self.x == 0 and self.y == world_radius,
                self.x == world_radius and self.y == 0,
                self.x == 0 and self.y == -world_radius,
                self.x == -world_radius and self.y == 0
            )
            x_upper = self.x == self_border.x_upper
            x_lower = self.x == self_border.x_lower
            y_upper = self.y == self_border.y_upper
            y_lower = self.y == self_border.y_lower
            conditions = (
                (y_upper and not x_upper) or corners[0],
                x_upper and y_upper,
                (x_upper and not y_upper) or corners[1],
                (y_lower and not x_lower) or corners[2],
                x_lower and y_lower,
                (x_lower and not y_lower) or corners[3]
            )

            def fix_position() -> tuple[int, int]:
                if conditions[border_0]:
                    position_x = x + mirrors[border_0][0] - self.neighbour_offsets[border_0][0]
                    position_y = y + mirrors[border_0][1] - self.neighbour_offsets[border_0][1]
                elif conditions[border_1]:
                    position_x = x + mirrors[border_1][0] - self.neighbour_offsets[border_1][0]
                    position_y = y + mirrors[border_1][1] - self.neighbour_offsets[border_1][1]
                else:
                    position_x = x
                    position_y = y
                return position_x, position_y

            border_0 = direction
            border_1 = (direction + 1) % 6
            if direction == 0:
                if y > neighbour_border.y_upper:
                    x, y = fix_position()
            elif direction == 1:
                if x > neighbour_border.x_upper:
                    x, y = fix_position()
            elif direction == 2:
                if x > neighbour_border.x_upper and y < neighbour_border.y_lower:
                    x, y = fix_position()
            elif direction == 3:
                if y < neighbour_border.y_lower:
                    x, y = fix_position()
            elif direction == 4:
                if x < neighbour_border.x_lower:
                    x, y = fix_position()
            elif direction == 5:
                if x < neighbour_border.x_lower and y > neighbour_border.y_upper:
                    x, y = fix_position()
            self.neighbours.append(all_tiles[x][y])
