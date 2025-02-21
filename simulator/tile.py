import math
from typing import Any, TYPE_CHECKING

from arcade import color
from arcade.types import Color

from core.service.coordinates import Coordinates, NEIGHBOUR_OFFSETS
from core.service.object import PhysicalObject, ProjectionObject
from simulator.world_object import WorldObject


if TYPE_CHECKING:
    from simulator.world import Map, Region, Tiles2


class TileProjection(ProjectionObject):
    main_color: Color = color.WHITE
    selected_color: Color = color.GRAY

    def __init__(self, tile: "Tile", coordinates: Coordinates) -> None:
        self.tile = tile
        self.real_coordinates = coordinates
        super().__init__()
        self.selected = False

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{self.real_coordinates}"

    def init(self, offset_x: float, offset_y: float, coeff: float, tilt_coeff: float) -> None:
        sqrt = math.sqrt(3)

        radius = coeff / 2
        width = sqrt * radius
        height = (2 * radius) * tilt_coeff
        self.size = (width, height)
        self.center_x = (sqrt * self.real_coordinates.x + sqrt / 2 * self.real_coordinates.y) * radius + offset_x
        self.center_y = (3 / 2 * self.real_coordinates.y) * radius * tilt_coeff + offset_y
        self.position = (self.center_x, self.center_y)

    def select(self, world_map: "Map") -> None:
        world_map.selected_tiles.add(self)
        self.color = self.selected_color
        self.selected = True

    def deselect(self, world_map: "Map") -> None:
        world_map.selected_tiles.remove(self)
        self.color = self.main_color
        self.selected = False

    def on_click(self, world_map: "Map") -> None:
        if self.selected:
            self.deselect(world_map)
        else:
            self.select(world_map)


class Tile(PhysicalObject):
    neighbours: list["Tile"]

    def __init__(self, coordinates: Coordinates, region: "Region") -> None:
        super().__init__()
        self.coordinates = coordinates
        self.x = self.coordinates.x
        self.y = self.coordinates.y

        self.a = self.coordinates.a
        self.b = self.coordinates.b
        self.c = self.coordinates.c

        self.projection = TileProjection(self, self.coordinates)

        # объект, занимающий этот тайл
        self.object: WorldObject | None = None
        self.region = region

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.coordinates})"

    # https://www.redblobgames.com/grids/hexagons/#wraparound
    def init(self, tiles_2: "Tiles2") -> Any:
        self.neighbours = []

        for direction, offset in NEIGHBOUR_OFFSETS.items():
            neighbour_coordinates = (self.coordinates + offset).fix_to_cycle(tiles_2)
            neighbour = tiles_2[neighbour_coordinates.x][neighbour_coordinates.y]
            self.neighbours.append(neighbour)
