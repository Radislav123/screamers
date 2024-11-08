from arcade import color

from simulator.world_object import WorldObject, WorldObjectSprite


class BaseSprite(WorldObjectSprite):
    color = color.RED_BROWN


class Base(WorldObject):
    sprite_class = BaseSprite

    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__(position_x, position_y)
