import random
from typing import Any, Sequence, TYPE_CHECKING

from arcade import color

from core.service.coordinates import Coordinates
from simulator.tile import Tile
from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.base import Base
    from simulator.region import Region
    from simulator.world import BaseSet, Regions2


class CreatureProjection(WorldObjectProjection):
    def __init__(self) -> None:
        super().__init__()
        self.color = color.APRICOT


class Creature(WorldObject):
    projection_class = CreatureProjection
    projections: dict["Tile", projection_class]
    is_creature = True

    def __init__(self, center_tile: "Tile", time: int, bases: Sequence["Base"]) -> None:
        super().__init__(center_tile, time)
        self.start_base, self.finish_base = random.sample(bases, 2)
        self.scream_radius = 10
        self.hear_radius = 10
        self.direction_reset_period = 100
        self.direction_change_timer = time
        self.last_hear_distance = self.hear_radius + 1
        self.last_hear_coordinates: Coordinates | None = None
        self.last_hear_self_coordinates: Coordinates | None = None
        self.base_reach_counter = 0

    def on_update(self, time: int, region: "Region", regions_2: "Regions2", bases: "BaseSet") -> Any:
        delta_time = time - self.last_acting_time
        self.last_acting_time = time
        if self.direction_change_timer > self.direction_reset_period:
            self.direction_change_timer = 0
            if self.last_hear_coordinates is not None:
                vector = self.last_hear_coordinates - self.last_hear_self_coordinates
                a, b, c = vector.to_3
                abs_a, abs_b, abs_c = abs(a), abs(b), abs(c)
                farthest = max(abs_a, abs_b, abs_c)
                if farthest == abs_a:
                    if a >= 0:
                        self.direction = 0
                    else:
                        self.direction = 3
                elif farthest == abs_b:
                    if b >= 0:
                        self.direction = 1
                    else:
                        self.direction = 4
                else:
                    if c >= 0:
                        self.direction = 2
                    else:
                        self.direction = 5
            else:
                self.direction = random.randint(0, 5)

        action = self.move
        action.timer += delta_time

        if action.timer >= action.period:
            blocker = action.execute(self)
            action.timer -= action.period
            if blocker is None:
                pass
            elif blocker is self.finish_base:
                self.base_reach_counter = -1
                self.direction = (self.direction + 3) % 6
                self.start_base = self.finish_base
                while self.start_base == self.finish_base:
                    self.finish_base = random.choice(bases)
            elif blocker.is_base:
                self.direction = (self.direction + 3) % 6

        for creature in region.get_creatures(self.scream_radius, regions_2):
            distance = self.center_tile.coordinates.distance_3(creature.center_tile.coordinates)
            if (distance <= self.scream_radius and distance <= creature.hear_radius
                    and (creature.last_hear_coordinates is None or distance <= creature.last_hear_distance)):
                creature.last_hear_distance = distance
                creature.last_hear_coordinates = self.center_tile.coordinates
                creature.last_hear_self_coordinates = creature.center_tile.coordinates

        self.age += delta_time
        self.direction_change_timer += delta_time
        self.last_hear_coordinates = None
        self.last_hear_self_coordinates = None
        self.last_hear_distance = self.hear_radius + 1
        self.base_reach_counter += 1
