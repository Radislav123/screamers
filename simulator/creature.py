from arcade import Sprite

from core.service.object import Object, PhysicalObject


class CreatureSprite(Sprite, Object):
    pass


class Creature(PhysicalObject):
    scream_radius = 10

    def __init__(self, position_x: int, position_y: int) -> None:
        super().__init__(position_x, position_y)
        self.resources = 0
        self.sprite = CreatureSprite()
