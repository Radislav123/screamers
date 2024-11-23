import random
from typing import Any, TYPE_CHECKING

from arcade import color

from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.tile import Tile


class BaseProjection(WorldObjectProjection):
    def __init__(self) -> None:
        super().__init__()
        self.color = color.RED_BROWN


class Base(WorldObject):
    projection_class = BaseProjection
    projections: dict["Tile", projection_class]
    radius = 5
    is_base = True

    def on_update(self, time: int) -> Any:
        delta_time = time - self.last_acting_time
        self.last_acting_time = time
        # todo: добавить перемещение к "выбранным" целям
        self.direction = random.randint(0, 5)

        action = self.move
        action.timer += delta_time

        if action.timer >= action.period:
            action.execute(self)
            action.timer -= action.period

        self.age += delta_time
