import random
from typing import Any, TYPE_CHECKING

from arcade import color

from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.tile import Tile


class BaseProjection(WorldObjectProjection):
    main_color = color.RED_BROWN


class Base(WorldObject):
    projection_class = BaseProjection
    projections: dict["Tile", projection_class]
    radius = 5
    is_base = True

    # todo: добавить базе крик, чтобы близкопроходящие букашки могли ее найти
    def __init__(self, center_tile: "Tile", time: int) -> None:
        super().__init__(center_tile, time)
        self.direction_reset_period = 200

    def on_update(self, time: int) -> Any:
        delta_time = time - self.last_acting_time
        self.last_acting_time = time
        if self.direction_reset_timer > self.direction_reset_period:
            self.direction_reset_timer = 0
            self.direction = random.randint(0, 5)

        action = self.move
        action.timer += delta_time

        if action.timer >= action.period:
            move = False
            if move:
                action.execute(self)
            action.timer -= action.period

        self.age += delta_time
        self.direction_reset_timer += delta_time
