from typing import Any, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from simulator.world_object import WorldObject


class Action:
    def __init__(self) -> None:
        self.period: float | None = 10
        self.timer: float = 0

    def execute(self, world_object: "WorldObject", *args, **kwargs) -> Any:
        pass


class Move(Action):
    def execute(self, world_object: "WorldObject", *args, **kwargs) -> Union["WorldObject", None]:
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

            old_region = world_object.center_tile.region
            world_object.center_tile = world_object.center_tile.neighbours[world_object.direction]
            new_region = world_object.center_tile.region
            world_object.projections = projections
            world_object.tiles = set(world_object.projections)

            if old_region != new_region:
                old_region.world_objects[world_object.__class__].remove(world_object)
                new_region.world_objects[world_object.__class__].add(world_object)

        return blocker
