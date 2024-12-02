import copy
from typing import Iterable, Self, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from simulator.world import Regions2, Tiles2


class Coordinates:
    radius_in_regions: int = None
    region_radius: int = None
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

    # todo: add inplace operators
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

    def reset(self) -> None:
        self.x = ABSOLUTE_CENTER.x
        self.y = ABSOLUTE_CENTER.y

        self.a = ABSOLUTE_CENTER.a
        self.b = ABSOLUTE_CENTER.b
        self.c = ABSOLUTE_CENTER.c

        self.to_2 = ABSOLUTE_CENTER.to_2
        self.to_3 = ABSOLUTE_CENTER.to_3

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
            value = max(self.to_3)
        else:
            value = max(abs(self.a - offset.a), abs(self.b - offset.b), abs(self.c - offset.c))
        return value == radius

    def get_distances(self, others: Iterable[Self], cycled: bool = False) -> dict[Self, int]:
        return {x: self.distance_3(x, cycled) for x in others}

    def get_sorted_distances(
            self,
            others: Iterable[Self],
            cycled: bool = False,
            reverse: bool = False
    ) -> list[tuple[Self, int]]:
        return sorted(self.get_distances(others, cycled).items(), key = lambda x: x[1], reverse = reverse)

    @classmethod
    def get_first_mirror(cls, center_offset: Self = None) -> Self:
        if center_offset is None:
            center_offset = ABSOLUTE_CENTER
        offset = cls.region_radius * 2 + 1
        x = -cls.region_radius + cls.radius_in_regions + center_offset.x
        y = offset + cls.radius_in_regions * (offset + cls.region_radius) + center_offset.y
        return cls(x, y)

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

    def fix_to_cycle(self, tiles_2: "Tiles2") -> Self:
        """Зацикливает координаты"""

        if self.x in tiles_2 and self.y in tiles_2[self.x]:
            instance = self
        else:
            mirrors = self.get_mirror_centers(self.get_first_mirror())
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
        # не учитывается зацикленность мира
        # return math.dist(self.to_2, other.to_2)
        raise NotImplementedError()

    def distance_3(self, other: "Self", cycled: bool = False) -> int:
        """Количество шагов через границы тайлов, чтобы попасть из одного в другой"""

        if cycled:
            first_mirror = ABSOLUTE_CENTER.get_first_mirror()
            mirrors = other.get_mirror_centers(first_mirror)
            distances = self.get_sorted_distances(x + other for x in mirrors)
            value = min(distances[0][1], self.distance_3(other, False))
        else:
            a = self.a - other.a
            if a < 0:
                a = -a
            b = self.b - other.b
            if b < 0:
                b = -b
            c = self.c - other.c
            if c < 0:
                c = -c
            if a > b:
                if a > c:
                    value = a
                else:
                    value = c
            else:
                if b > c:
                    value = b
                else:
                    value = c

        return value

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
    0: Coordinates.from_3(1, -1, 0),
    1: Coordinates.from_3(0, -1, 1),
    2: Coordinates.from_3(-1, 0, 1),
    3: Coordinates.from_3(-1, 1, 0),
    4: Coordinates.from_3(0, 1, -1),
    5: Coordinates.from_3(1, 0, -1)
}
