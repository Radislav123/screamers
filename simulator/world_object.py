import arcade
from arcade.types import Color, RGBA

from core.service.object import PhysicalObject, ProjectionObject
from simulator.tile import TileProjection


class WorldObjectProjection(ProjectionObject):
    tile_projection: TileProjection
    color: Color | RGBA

    def init(self) -> None:
        self.shape = arcade.shape_list.create_polygon(self.tile_projection.border_points, self.color)
        self.inited = True


class WorldObject(PhysicalObject):
    projection_class: type[WorldObjectProjection]

    def __init__(self, tile) -> None:
        self.tile = tile
        self.resources = 0
        super().__init__(self.tile.x, self.tile.y)

        self.projection = self.projection_class()
