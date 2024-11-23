from typing import Any, Iterable, TYPE_CHECKING

from arcade.shape_list import create_polygon
from arcade.types import Color, RGBA

from core.service.object import PhysicalObject, ProjectionObject
from simulator.action import Move


if TYPE_CHECKING:
    from simulator.tile import Tile, TileProjection


class WorldObjectProjection(ProjectionObject):
    tile_projection: "TileProjection"
    color: Color | RGBA

    def init(self) -> None:
        self.shape = create_polygon(self.tile_projection.border_points, self.color)
        self.inited = True


class WorldObject(PhysicalObject):
    projection_class: type[WorldObjectProjection]
    projections: dict["Tile", WorldObjectProjection]
    is_base = False
    is_creature = False

    def __init__(self, center_tile: "Tile", time: int) -> None:
        super().__init__()
        self.center_tile = center_tile
        self.tiles: set["Tile"] | None = None
        self.age = 0
        self.direction: int = 0
        self.resources = 0
        self.last_acting_time = time
        self.act_period = 5
        self.act_remainder = self.id % self.act_period

        self.move = Move()

    def init(self, tiles: Iterable["Tile"]) -> Any:
        self.tiles = set(tiles)
        self.projections = {}
        for tile in self.tiles:
            tile.object = self
            projection = self.projection_class()
            self.projections[tile] = projection
            projection.tile_projection = tile.projection
