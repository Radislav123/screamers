import math
from typing import Any, TYPE_CHECKING

from core.service.coordinates import Coordinates, NEIGHBOUR_OFFSETS
from core.service.object import PhysicalObject, ProjectionObject
from simulator.world_object import WorldObject


if TYPE_CHECKING:
    from simulator.world import Map, Region, Tiles2


class TileProjection(ProjectionObject):
    def __init__(self, coordinates: Coordinates) -> None:
        self.real_coordinates = coordinates
        super().__init__()
        self.selected = False

    def __repr__(self) -> str:
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
        self.selected = True

    def deselect(self, world_map: "Map") -> None:
        world_map.selected_tiles.remove(self)
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

        self.projection = TileProjection(self.coordinates)

        self.object: WorldObject | None = None
        self.region = region

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.coordinates})"

    # https://www.redblobgames.com/grids/hexagons/#wraparound
    def init(self, tiles_2: "Tiles2", radius_in_regions: int, region_radius: int) -> Any:
        self.neighbours = []

        for direction, offset in NEIGHBOUR_OFFSETS.items():
            neighbour_coordinates = (self.coordinates + offset).fix_to_cycle(tiles_2, radius_in_regions, region_radius)
            neighbour = tiles_2[neighbour_coordinates.x][neighbour_coordinates.y]
            self.neighbours.append(neighbour)
