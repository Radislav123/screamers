import copy
from collections import defaultdict
from typing import Any, Self, TYPE_CHECKING, Type

from sortedcontainers import SortedSet

from core.service.coordinates import Coordinates
from core.service.object import PhysicalObject, ProjectionObject
from simulator.base import Base
from simulator.creature import Creature
from simulator.tile import Tile, TileProjection
from simulator.world_object import WorldObject


if TYPE_CHECKING:
    from simulator.world import BaseSet, Regions2, Tiles2


class RegionProjection(ProjectionObject):
    tile_projection: TileProjection


class Region(PhysicalObject):
    projection_class = RegionProjection
    projections: dict[Tile, projection_class]
    neighbours: list[Self]
    radius: int = None

    def __init__(self, coordinates: Coordinates) -> None:
        super().__init__()
        self.coordinates = coordinates
        self.x = self.coordinates.x
        self.y = self.coordinates.y

        self.a = self.coordinates.a
        self.b = self.coordinates.b
        self.c = self.coordinates.c

        self.tiles: set[Tile] | None = None
        self.neighbour_layers: dict[int, set[Self]] = {}
        # todo: разделить
        self.world_objects: dict[Type[WorldObject], set[WorldObject] | SortedSet[WorldObject]] = defaultdict(SortedSet)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.coordinates})"

    def init(self, radius_in_regions: int, tiles_2: "Tiles2", regions_2: "Regions2") -> Any:
        self.projections = {}
        for tile in self.tiles:
            projection = self.projection_class()
            self.projections[tile] = projection
            projection.tile_projection = tile.projection

        first_mirror = self.coordinates.get_first_mirror(0, self.radius, self.coordinates)
        first_mirror_fixed = first_mirror.fix_to_cycle(tiles_2, radius_in_regions, self.radius)
        mirror_centers = self.coordinates.get_mirror_centers(first_mirror_fixed, self.coordinates)
        neighbour_indexes = [index.fix_to_cycle(tiles_2, radius_in_regions, self.radius) for index in mirror_centers]
        self.neighbours = [regions_2[index.x][index.y] for index in neighbour_indexes]

    def on_update(self, delta_time: int, time: int, regions_2: "Regions2", bases: "BaseSet") -> Any:
        for base in self.world_objects[Base]:
            base.on_update(time)
        for creature in self.world_objects[Creature]:
            creature.on_update(time, self, regions_2, bases)

    def get_creatures(self, radius: int, regions_2: "Regions2") -> set[Creature]:
        # noinspection PyTypeChecker
        creatures: set[Creature] = copy.copy(self.world_objects[Creature])
        layers = radius // self.radius + 1

        if layers not in self.neighbour_layers:
            region_indexes = set()
            region_indexes.add(self.coordinates)
            region_indexes = Coordinates.append_layers(regions_2, region_indexes, layers, True)
            regions = set(regions_2[index.x][index.y] for index in region_indexes)
            self.neighbour_layers[layers] = regions
        regions = self.neighbour_layers[layers]

        for region in regions:
            creatures.update(region.world_objects[Creature])

        return creatures
