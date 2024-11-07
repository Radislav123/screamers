from arcade import Sprite

from core.service.object import PhysicalObject, ProjectionObject


class BaseSprite(Sprite, ProjectionObject):
    pass


class Base(PhysicalObject):
    counter = 0

    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__(position_x, position_y)
        self.resources = 0
        self.sprite = BaseSprite()
