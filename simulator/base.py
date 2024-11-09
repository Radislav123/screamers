from arcade import color

from simulator.world_object import WorldObject, WorldObjectProjection


class BaseProjection(WorldObjectProjection):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = color.RED_BROWN


class Base(WorldObject):
    projection_class = BaseProjection
