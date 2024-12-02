import random
from typing import Any, Sequence, TYPE_CHECKING

from arcade import color

from core.service.coordinates import Coordinates, NEIGHBOUR_OFFSETS
from simulator.tile import Tile
from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.base import Base
    from simulator.region import Region
    from simulator.world import BaseSet, Regions2


class CreatureProjection(WorldObjectProjection):
    main_color = color.APRICOT


class Creature(WorldObject):
    projection_class = CreatureProjection
    projections: dict["Tile", projection_class]
    is_creature = True
    # todo: remove temp
    temp = 0

    def __init__(self, center_tile: "Tile", time: int, bases: Sequence["Base"]) -> None:
        super().__init__(center_tile, time)
        if len(bases) > 1:
            self.start_base, self.finish_base = random.sample(bases, 2)
        else:
            self.start_base = bases[0]
            self.finish_base = bases[0]
        # todo: set to 10?
        self.scream_radius = 100
        self.hear_radius = 100
        self.heard = False
        self.last_hear_distance = self.hear_radius + 1
        self.reference_direction_vector: Coordinates | None = None
        self.direction_vector: Coordinates | None = None
        self.path_vector: Coordinates | None = None
        self.last_hear_coordinates: Coordinates | None = None
        self.last_hear_self_coordinates: Coordinates | None = None
        self.base_reach_counter = 0

    def on_update(self, time: int, region: "Region", regions_2: "Regions2", bases: "BaseSet") -> Any:
        delta_time = time - self.last_acting_time
        self.last_acting_time = time

        if self.heard and self.direction_correct_timer >= self.direction_correct_period:
            self.direction_correct_timer -= self.direction_correct_period
            if self.reference_direction_vector is None:
                self.reference_direction_vector = self.last_hear_coordinates - self.last_hear_self_coordinates
                self.direction_vector = self.reference_direction_vector.copy()
                self.path_vector = Coordinates(0, 0)
            else:
                if (abs(self.path_vector.a) > abs(self.direction_vector.a)
                        or abs(self.path_vector.b) > abs(self.direction_vector.b)
                        or abs(self.path_vector.c) > abs(self.direction_vector.c)):
                    self.direction_vector += self.reference_direction_vector
            a = self.direction_vector.a - self.path_vector.a
            b = self.direction_vector.b - self.path_vector.b
            c = self.direction_vector.c - self.path_vector.c
            abs_a = abs(a)
            abs_b = abs(b)
            abs_c = abs(c)
            farthest = max(abs_a, abs_b, abs_c)
            if farthest == abs_a:
                if a >= 0:
                    self.direction = 0
                else:
                    self.direction = 3
            elif farthest == abs_b:
                if b >= 0:
                    self.direction = 4
                else:
                    self.direction = 1
            else:
                if c >= 0:
                    self.direction = 2
                else:
                    self.direction = 5

        action = self.move
        action.timer += delta_time
        if action.timer >= action.period:
            blocker = action.execute(self)
            action.timer -= action.period
            if blocker is None:
                if self.reference_direction_vector is not None:
                    self.path_vector += NEIGHBOUR_OFFSETS[self.direction]
            elif blocker is self.finish_base:
                self.__class__.temp += 1
                print(self.temp)
                self.base_reach_counter = 0
                self.reset_hear_attributes(False)
                self.turn_around()
                if len(bases) > 1:
                    self.start_base = self.finish_base
                    while self.start_base == self.finish_base:
                        self.finish_base: Base = random.choice(bases)
            elif blocker.is_base:
                self.__class__.temp -= 1
                self.turn_right()
            elif blocker.is_creature:
                self.direction = (self.direction + 1) % 6
                new_blocker = action.execute(self)
                if self.reference_direction_vector is not None and new_blocker is None:
                    self.path_vector += NEIGHBOUR_OFFSETS[self.direction]
                self.direction = (self.direction - 1) % 6

        if self.direction_reset_timer >= self.direction_reset_period:
            self.direction_reset_timer -= self.direction_reset_period
            self.reset_hear_attributes()

        for other in region.get_creatures(self.scream_radius, regions_2):
            if other is not self and self.start_base == other.finish_base:
                distance = (self.center_tile.coordinates.distance_3(other.center_tile.coordinates, True)
                            + self.base_reach_counter)
                if (distance < other.last_hear_distance and
                        distance <= self.scream_radius and distance <= other.hear_radius):
                    other.last_hear_distance = distance
                    other.last_hear_coordinates = self.center_tile.coordinates
                    other.last_hear_self_coordinates = other.center_tile.coordinates
                    other.heard = True

        self.age += delta_time
        self.direction_reset_timer += delta_time
        self.direction_correct_timer += delta_time

    def turn_right(self) -> None:
        self.direction = (self.direction + 1) % 6
        if self.reference_direction_vector:
            self.reference_direction_vector = self.reference_direction_vector.rotate_60()
            self.direction_vector = self.reference_direction_vector.copy()
            self.path_vector.reset()

    def turn_around(self) -> None:
        self.direction = (self.direction + 3) % 6
        if self.reference_direction_vector:
            self.reference_direction_vector *= -1
            self.direction_vector = self.reference_direction_vector.copy()
            self.path_vector.reset()

    def reset_hear_attributes(self, reset_direction: bool = True) -> None:
        self.heard = False
        self.direction_reset_timer = 0
        self.direction_correct_timer = 0
        self.last_hear_distance = self.hear_radius + 1
        if reset_direction:
            self.reference_direction_vector = None
            self.direction_vector = None
            self.path_vector = None
        self.last_hear_coordinates = None
        self.last_hear_self_coordinates = None
