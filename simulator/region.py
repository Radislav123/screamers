from typing import Any, Iterable

from core.service.coordinates import Coordinates
from core.service.object import PhysicalObject, ProjectionObject
from simulator.base import Base
from simulator.creature import Creature
from simulator.tile import Tile, TileProjection


class RegionProjection(ProjectionObject):
    tile_projection: TileProjection


class Region(PhysicalObject):
    projection_class = RegionProjection
    projections: dict[Tile, projection_class]
    radius: int = None

    def __init__(self, coordinates: Coordinates, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.coordinates = coordinates
        self.x = self.coordinates.x
        self.y = self.coordinates.y

        self.a = self.coordinates.a
        self.b = self.coordinates.b
        self.c = self.coordinates.c

        self.tiles: set[Tile] | None = None
        self.creatures = set[Creature]()
        self.bases = set[Base]()

    def init(self, tiles: Iterable[Tile]) -> Any:
        self.tiles = set(tiles)
        self.projections = {}
        for tile in self.tiles:
            projection = self.projection_class()
            self.projections[tile] = projection
            projection.tile_projection = tile.projection

    def on_update(self, *args, **kwargs) -> Any:
        for creature in self.creatures:
            creature.on_update(*args, **kwargs)
        for base in self.bases:
            base.on_update(*args, **kwargs)
