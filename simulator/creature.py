import random
from typing import Any, Sequence, TYPE_CHECKING, Union

from arcade import color

from core.service.coordinates import Coordinates
from simulator.tile import Tile
from simulator.world_object import WorldObject, WorldObjectProjection


if TYPE_CHECKING:
    from simulator.base import Base
    from simulator.world import BaseSet, Regions2


class CreatureProjection(WorldObjectProjection):
    main_color = color.APRICOT


class Creature(WorldObject):
    projection_class = CreatureProjection
    projections: dict["Tile", projection_class]
    is_creature = True

    def __init__(self, center_tile: "Tile", time: int, bases: Sequence["Base"]) -> None:
        super().__init__(center_tile, time)
        if len(bases) > 1:
            self.start_base, self.finish_base = random.sample(bases, 2)
        else:
            self.start_base = bases[0]
            self.finish_base = bases[0]
        self.scream_radius = 10
        self.hear_radius = 100

        # эталон направления движения
        self.reference_direction_vector = Coordinates(random.randint(-10, 10), random.randint(-10, 10))
        # направление движения
        self.direction_vector = Coordinates(0, 0)
        # пройденный путь
        self.path_vector: Coordinates = Coordinates(0, 0)
        self.bases_reach_counter = {base: 0 for base in bases}
        self.heard_distance: int | None = None
        self.heard_tile: Union["Tile", None] = None

    def set_direction(self) -> None:
        if self.heard_distance is not None:
            self.reference_direction_vector = self.heard_tile.coordinates - self.center_tile.coordinates
            self.direction_vector = self.reference_direction_vector.copy()
            self.path_vector.reset()
            self.heard_distance = None
            self.heard_tile = None
        if (abs(self.path_vector.a) >= abs(self.direction_vector.a)
                or abs(self.path_vector.b) >= abs(self.direction_vector.b)
                or abs(self.path_vector.c) >= abs(self.direction_vector.c)):
            self.direction_vector += self.reference_direction_vector

        a = self.direction_vector.a - self.path_vector.a
        b = self.direction_vector.b - self.path_vector.b
        c = self.direction_vector.c - self.path_vector.c
        # offset - нужен, чтобы вес был > 0
        offset = 0.000001
        abs_a = abs(a) + offset
        abs_b = abs(b) + offset
        abs_c = abs(c) + offset
        farthest = random.choices((a, b, c), (abs_a, abs_b, abs_c))[0]
        if farthest == a:
            if a >= 0:
                self.direction = 0
            else:
                self.direction = 3
        elif farthest == b:
            if b >= 0:
                self.direction = 4
            else:
                self.direction = 1
        else:
            if c >= 0:
                self.direction = 2
            else:
                self.direction = 5

        if random.randint(0, 99) > 95:
            self.direction = (self.direction + random.choice((-1, 1))) % 6

    def on_update(self, time: int, regions_2: "Regions2", bases: "BaseSet") -> Any:
        delta_time = time - self.last_acting_time
        self.last_acting_time = time

        old_coordinates = self.center_tile.coordinates
        if time % 1 == 0:
            self.set_direction()
        blocker = self.move.execute(self)
        # Достиг финальной базы
        temp = False
        if blocker == self.finish_base:
            self.bases_reach_counter[self.finish_base] = -delta_time
            self.start_base = self.finish_base
            temp = True
            while len(bases) > 1 and self.finish_base == self.start_base:
                self.finish_base = random.choice(bases)
            self.turn_around()
        # Попытка обойти справа
        elif blocker is not None:
            turn_around = True
            if turn_around:
                self.turn_around()
                self.move.execute(self)
            else:
                old_direction = self.direction
                self.direction = (self.direction + 1) % 6
                self.move.execute(self)
                self.direction = old_direction
        self.path_vector += self.center_tile.coordinates - old_coordinates

        self.cry(regions_2, temp)
        self.age += delta_time
        self.bases_reach_counter = {base: counter + delta_time for base, counter in self.bases_reach_counter.items()}

    def cry(self, regions_2: "Regions2", temp: bool) -> None:
        for other in self.center_tile.region.get_creatures(self.scream_radius, regions_2):
            if self is not other:
                crier_distance = self.center_tile.coordinates.distance_3(other.center_tile.coordinates, True)
                base_distance = crier_distance + self.bases_reach_counter[other.finish_base]
                if (crier_distance <= other.hear_radius and
                        (other.heard_distance is None or base_distance < other.heard_distance)):
                    other.heard_distance = base_distance
                    other.heard_tile = self.center_tile

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
