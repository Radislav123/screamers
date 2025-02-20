import random
from typing import Any, TYPE_CHECKING

from arcade import color

from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.tile import Tile
    from simulator.world import Regions2


class BaseProjection(WorldObjectProjection):
    main_color = color.RED_BROWN


class Base(WorldObject):
    projection_class = BaseProjection
    projections: dict["Tile", projection_class]
    radius = 10
    is_base = True

    def __init__(self, center_tile: "Tile", time: int) -> None:
        super().__init__(center_tile, time)
        self.direction_reset_period = 200
        self.scream_radius = 10

    def on_update(self, time: int, regions_2: "Regions2") -> Any:
        delta_time = time - self.last_acting_time
        self.last_acting_time = time
        self.direction = random.randint(0, 5)

        action = self.move
        action.timer += delta_time

        if action.timer >= action.period:
            # todo: базы должны двигаться медленнее, плавнее и периодически выбирать себе направление,
            #  чтобы движение не было столь хаотичным
            move = False
            if move:
                action.execute(self)
            action.timer -= action.period

        self.age += delta_time
