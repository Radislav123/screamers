from arcade import Sprite

from core.service.object import PhysicalObject, ProjectionObject


class CreatureSprite(Sprite, ProjectionObject):
    pass


class Creature(PhysicalObject):
    scream_radius = 10

    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__(position_x, position_y)
        self.resources = 0
        self.sprite = CreatureSprite()
