import copy
from typing import Any, TYPE_CHECKING

from arcade.shape_list import create_polygon
from arcade.types import Color, RGBA

from core.service.object import PhysicalObject, ProjectionObject


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
    projections: set["projection_class"]
    radius = 0

    def __init__(self, center_tile: "Tile", *args, **kwargs) -> None:
        self.center_tile = center_tile
        self.tiles: set["Tile"] | None = None
        self.resources = 0
        super().__init__(self.center_tile.x, self.center_tile.y, *args, **kwargs)

    def init(self, tiles: set["Tile"]) -> Any:
        self.tiles = tiles
        self.projections = set()
        for tile in self.tiles:
            tile.object = self
            projection = self.projection_class()
            self.projections.add(projection)
            projection.tile_projection = tile.projection

    @staticmethod
    def append_layers(tiles: set["Tile"], layers_number: int) -> set["Tile"]:
        tiles = copy.copy(tiles)
        for _ in range(layers_number):
            new_tiles = set()
            for tile in tiles:
                new_tiles.add(tile)
                new_tiles.update(tile.neighbours)
            tiles = new_tiles
        return tiles
