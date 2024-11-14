import copy
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
    radius = 0

    def __init__(self, center_tile: "Tile", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.center_tile = center_tile
        self.tiles: set["Tile"] | None = None
        self.resources = 0

        self.move = Move()

    def init(self, tiles: Iterable["Tile"]) -> Any:
        self.tiles = set(tiles)
        self.projections = {}
        for tile in self.tiles:
            tile.object = self
            projection = self.projection_class()
            self.projections[tile] = projection
            projection.tile_projection = tile.projection

    def on_update(self, *args, **kwargs) -> Any:
        action = self.move
        action.executed = False
        action.timer += 1
        if action.timer >= action.period:
            action.timer -= action.period
            action.execute(self)
