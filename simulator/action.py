from typing import Any, TYPE_CHECKING, Union

from core.service.object import Object


if TYPE_CHECKING:
    from simulator.base import Base
    from simulator.creature import Creature
    from simulator.world_object import WorldObject


class Action(Object):
    def __init__(self) -> None:
        super().__init__()
        self.period: float | None = (self.id % 3) + 3
        self.timer: float = 0

    def execute(self, world_object: Union["Base", "Creature"]) -> Any:
        pass


class Move(Action):
    def execute(self, world_object: Union["Base", "Creature"]) -> Union["WorldObject", None]:
        projections = {}
        blocker = None
        for tile in world_object.tiles:
            new_tile = tile.neighbours[world_object.direction]
            if new_tile.object is None or new_tile.object is world_object:
                projections[new_tile] = world_object.projections[tile]
            else:
                blocker = new_tile.object
                break
        else:
            for tile in world_object.tiles:
                tile.object = None
            for new_tile, projection in projections.items():
                new_tile.object = world_object
                projection.tile_projection = new_tile.projection
                projection.position = new_tile.projection.position

            old_region = world_object.center_tile.region
            world_object.center_tile = world_object.center_tile.neighbours[world_object.direction]
            new_region = world_object.center_tile.region
            world_object.projections = projections
            world_object.tiles = set(world_object.projections)

            if old_region != new_region:
                if world_object in old_region.bases:
                    old_region.bases.remove(world_object)
                    new_region.bases.append(world_object)
                else:
                    old_region.creatures.remove(world_object)
                    new_region.creatures.append(world_object)

        return blocker
