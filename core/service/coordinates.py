import copy
import math
from typing import Iterable, Self, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from simulator.world import Regions2, Tiles2


class Coordinates:
    mirror_centers: dict[tuple[Self, Self], list[Self]] = {}
    __slots__ = ["x", "y", "a", "b", "c", "to_2", "to_3"]

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

        self.a = x
        self.b = y
        self.c = -x - y

        self.to_2 = (self.x, self.y)
        self.to_3 = (self.a, self.b, self.c)

    def __hash__(self) -> int:
        return hash(self.to_2)

    def __eq__(self, other: Self) -> bool:
        return self.to_2 == other.to_2

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)

    def __repr__(self) -> Self:
        return f"{self.__class__.__name__}{self.to_2, self.to_3}"

    def __floordiv__(self, other: int) -> Self:
        return self.__class__(self.x // other, self.y // other)

    def __mul__(self, other: int) -> Self:
        return self.__class__(self.x * other, self.y * other)

    @classmethod
    def get_mirror_centers(cls, first_center: Self, offset: Self = None) -> list[Self]:
        if offset is None:
            offset = ABSOLUTE_CENTER
        key = (first_center, offset)
        if key not in cls.mirror_centers:
            centers = [first_center]
            instance = first_center - offset
            for index in range(5):
                instance = instance.rotate_60()
                centers.append(instance + offset)
            cls.mirror_centers[key] = centers
        centers = cls.mirror_centers[key]

        return centers

    def copy(self) -> Self:
        return copy.deepcopy(self)

    @classmethod
    def from_2(cls, x: int, y: int) -> Self:
        return cls(x, y)

    @classmethod
    def from_3(cls, a: int, b: int, c: int) -> Self:
        assert a + b + c == 0, "Coordinates are not correct"
        return cls(a, b)

    def in_radius(self, radius: int, offset: Self = None) -> bool:
        if offset is None:
            absolute = self
        else:
            absolute = self - offset
        return abs(absolute.a) < radius and abs(absolute.b) < radius and abs(absolute.c) < radius

    def out_radius(self, radius: int, offset: Self = None) -> bool:
        if offset is None:
            absolute = self
        else:
            absolute = self - offset
        return abs(absolute.a) > radius or abs(absolute.b) > radius or abs(absolute.c) > radius

    def on_radius(self, radius: int, offset: Self = None) -> bool:
        if offset is None:
            absolute = self
        else:
            absolute = self - offset
        values = sorted((abs(x) for x in absolute.to_3), reverse = True)
        return values[0] == radius

    def get_distances(self, others: Iterable[Self]) -> dict[Self, float]:
        return {x: self.distance_3(x) for x in others}

    def get_sorted_distances(self, others: Iterable[Self], reverse: bool = False) -> list[tuple[Self, float]]:
        return sorted(self.get_distances(others).items(), key = lambda x: x[1], reverse = reverse)

    @classmethod
    def get_first_mirror(cls, radius_in_regions: int, region_radius: int, center_offset: Self = None) -> Self:
        if center_offset is None:
            center_offset = ABSOLUTE_CENTER
        offset = region_radius * 2 + 1
        x = -region_radius + radius_in_regions + center_offset.x
        y = offset + radius_in_regions * (offset + region_radius) + center_offset.y
        return cls(x, y)

    def fix_to_cycle(self, tiles_2: "Tiles2", radius_in_regions: int, region_radius: int) -> Self:
        """Зацикливает координаты"""

        if self.x in tiles_2 and self.y in tiles_2[self.x]:
            instance = self
        else:
            mirrors = self.get_mirror_centers(self.get_first_mirror(radius_in_regions, region_radius))
            distances = self.get_sorted_distances(mirrors)
            closest = distances[0][0]
            instance = self - closest
        return instance

    def rotate_60(self, offset: Self = None) -> Self:
        if offset is None:
            instance = self.__class__.from_3(-self.b, -self.c, -self.a)
        else:
            absolute = self - offset
            instance = self.__class__.from_3(-absolute.b, -absolute.c, -absolute.a) + offset
        return instance

    def rotate_180(self, offset: Self = None) -> Self:
        if offset is None:
            instance = self.__class__.from_3(-self.a, -self.b, -self.c)
        else:
            absolute = self - offset
            instance = self.__class__.from_3(-absolute.a, -absolute.b, -absolute.c)
        return instance

    def distance_2(self, other: "Self") -> float:
        return math.dist(self.to_2, other.to_2)

    def distance_3(self, other: "Self") -> int:
        """Количество шагов через границы тайлов, чтобы попасть из одного в другой"""

        return sum(abs(x) for x in (self - other).to_3) // 2

    @staticmethod
    def append_layers(
            objects_2: Union["Tiles2", "Regions2", None],
            indexes: Iterable["Coordinates"],
            layers_number: int,
            real_neighbours: bool = True
    ) -> set["Coordinates"]:
        indexes = set(indexes)
        last_layer = indexes
        for _ in range(layers_number):
            new_layer = set()
            for index in last_layer:
                if real_neighbours:
                    new_indexes = (x.coordinates for x in objects_2[index.x][index.y].neighbours)
                else:
                    new_indexes = (index + offset for offset in NEIGHBOUR_OFFSETS.values())
                for new_index in new_indexes:
                    if new_index not in indexes:
                        new_layer.add(new_index)
            indexes.update(new_layer)
            last_layer = new_layer
        return indexes


ABSOLUTE_CENTER = Coordinates(0, 0)
NEIGHBOUR_OFFSETS = {
    0: Coordinates(0, 1),
    1: Coordinates(1, 0),
    2: Coordinates(1, -1),
    3: Coordinates(0, -1),
    4: Coordinates(-1, 0),
    5: Coordinates(-1, 1)
}
