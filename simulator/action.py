import random
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from simulator.world_object import WorldObject


class Action:
    def __init__(self) -> None:
        self.default_period: float | None = 1
        self.period: float | None = 1
        self.timer: float = 0
        self.executed = False

    def execute(self, world_object: "WorldObject", *args, **kwargs) -> None:
        pass


class Move(Action):
    def execute(self, world_object: "WorldObject", *args, **kwargs) -> None:
        direction = random.randint(0, world_object.center_tile.neighbours_amount - 1)
        projections = {}
        for tile in world_object.tiles:
            new_tile = tile.neighbours[direction]
            if new_tile.object is None or new_tile.object is world_object:
                projections[new_tile] = world_object.projections[tile]
            else:
                break
        else:
            for tile in world_object.tiles:
                tile.object = None
            for new_tile, projection in projections.items():
                new_tile.object = world_object
                projection.tile_projection = new_tile.projection

            world_object.center_tile = world_object.center_tile.neighbours[direction]
            world_object.projections = projections
            world_object.tiles = set(world_object.projections)
            self.executed = True
