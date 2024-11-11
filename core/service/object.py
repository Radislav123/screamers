import copy
import math
from typing import Any, Self

from arcade.shape_list import Shape

from core.service import settings
from core.service.logger import Logger


class Object:
    settings = settings.Settings()
    counter = 0

    def __new__(cls, *args, **kwargs) -> "Self":
        instance = super().__new__(cls)
        instance.logger = Logger(cls.__name__)
        return instance

    def __init__(self, *args, **kwargs) -> None:
        if args or kwargs:
            print(args, kwargs)
        super().__init__(*args, **kwargs)
        self.id = self.counter
        self.__class__.counter += 1

    def init(self, *args, **kwargs) -> Any:
        pass

    def start(self, *args, **kwargs) -> Any:
        pass

    def stop(self, *args, **kwargs) -> Any:
        pass


class ProjectionObject(Object):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.inited = False
        self.shape: Shape | None = None

    def on_draw(self, *args, **kwargs) -> Any:
        pass


class Coordinates:
    mirror_centers: dict[int, dict[int | None, "Self"]] = {}

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

        self.a = x
        self.b = y
        self.c = -x - y

        self.all = copy.copy(self.__dict__)

    def __add__(self, other: Self) -> Self:
        return Coordinates(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return Coordinates(self.x - other.x, self.y - other.y)

    def __repr__(self) -> Self:
        return f"{self.__class__.__name__}{self.all}"

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

    def to_2(self) -> tuple[int, int]:
        return self.x, self.y

    def to_3(self) -> tuple[int, int, int]:
        return self.a, self.b, self.c

    def in_radius(self, radius: int) -> bool:
        return abs(self.a) < radius and abs(self.b) < radius and abs(self.c) < radius

    def out_radius(self, radius: int) -> bool:
        return abs(self.a) > radius or abs(self.b) > radius or abs(self.c) > radius

    def on_radius(self, radius: int) -> bool:
        values = sorted((abs(x) for x in self.to_3()), reverse = True)
        return values[0] == radius

    def fix_to_cycle(self, radius: int) -> Self:
        """Зацикливает координаты"""

        mirrors = Coordinates.get_mirror_centers(radius)
        distances = sorted({x: self.distance_3(x) for x in mirrors.values()}.items(), key = lambda x: x[1])
        closest = distances[0][0]
        return self - closest

    def rotate_60(self) -> Self:
        return self.__class__.from_3(-self.b, -self.c, -self.a)

    def rotate_180(self) -> Self:
        return self.__class__.from_3(-self.a, -self.b, -self.c)

    def distance_2(self, other: "Self") -> float:
        return math.dist(self.to_2(), other.to_2())

    def distance_3(self, other: "Self") -> float:
        return sum(abs(x) for x in (self - other).to_3()) / 2


class PhysicalObject(Object):
    def __init__(self, coordinates: Coordinates, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.coordinates = coordinates.copy()
        self.x = self.coordinates.x
        self.y = self.coordinates.y

        self.a = self.coordinates.a
        self.b = self.coordinates.b
        self.c = self.coordinates.c

    def on_update(self, *args, **kwargs) -> Any:
        pass
