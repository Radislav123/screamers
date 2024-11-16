import copy
import math
from typing import Iterable, Self, TYPE_CHECKING


if TYPE_CHECKING:
    from simulator.world import Tiles2


class Coordinates:
    mirror_centers: dict[tuple[Self, Self], set[Self]] = {}

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

        self.a = x
        self.b = y
        self.c = -x - y

        self.all = copy.copy(self.__dict__)
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
        return f"{self.__class__.__name__}{self.all}"

    def __floordiv__(self, other: int) -> Self:
        return self.__class__(self.x // other, self.y // other)

    def __mul__(self, other: int) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def get_mirror_centers(self, offset: Self = None) -> set[Self]:
        if offset is None:
            offset = self.__class__(0, 0)
        key = (self, offset)
        if key not in self.mirror_centers:
            centers = set()
            instance = self - offset
            for index in range(6):
                instance = instance.rotate_60()
                centers.add(instance)
            self.mirror_centers[key] = centers
        centers = self.mirror_centers[key]

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

    def fix_to_cycle(self, tiles_2: "Tiles2", radius_in_regions: int, region_radius: int) -> Self:
        """Зацикливает координаты"""

        if self.x in tiles_2 and self.y in tiles_2[self.x]:
            instance = self
        else:
            offset = region_radius * 2 + 1
            x = -region_radius + radius_in_regions
            y = offset + radius_in_regions * (offset + region_radius)
            first_center = Coordinates(x, y)
            mirrors = first_center.get_mirror_centers()
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
