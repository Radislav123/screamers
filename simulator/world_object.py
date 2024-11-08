import arcade
from arcade.types import Color, RGBA

from core.service.object import PhysicalObject, ProjectionObject
from simulator.tile import TileProjection


class WorldObjectSprite(ProjectionObject):
    tile_projection: TileProjection
    polygon: arcade.shape_list.Shape
    color: Color | RGBA

    def init(self) -> None:
        self.polygon = arcade.shape_list.create_polygon(self.tile_projection.border_points, self.color)
        self.inited = True


class WorldObject(PhysicalObject):
    sprite_class: type[WorldObjectSprite]

    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__(position_x, position_y)
        self.resources = 0

        self.sprite = self.sprite_class()
