import copy
import math
from typing import Iterable, Self


class Coordinates:
    mirror_centers: dict[int, dict[int | None, "Self"]] = {}

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

    @classmethod
    def get_mirror_centers(cls, radius: int) -> dict[int | None, "Self"]:
        if radius not in cls.mirror_centers:
            next_center = Coordinates.from_3(radius * 2 + 1, -radius, -radius - 1)
            centers = {None: Coordinates(0, 0), 0: next_center}
            for index in range(1, 6):
                next_center = next_center.rotate_60()
                centers[index] = next_center
            cls.mirror_centers[radius] = centers

        return cls.mirror_centers[radius]

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

    def fix_to_cycle(self, radius: int) -> Self:
        """Зацикливает координаты"""

        mirrors = Coordinates.get_mirror_centers(radius)
        distances = self.get_sorted_distances(mirrors.values())
        closest = distances[0][0]
        return self - closest

    def rotate_60(self) -> Self:
        return self.__class__.from_3(-self.b, -self.c, -self.a)

    def rotate_180(self) -> Self:
        return self.__class__.from_3(-self.a, -self.b, -self.c)

    def distance_2(self, other: "Self") -> float:
        return math.dist(self.to_2, other.to_2)

    def distance_3(self, other: "Self") -> float:
        return sum(abs(x) for x in (self - other).to_3) / 2
