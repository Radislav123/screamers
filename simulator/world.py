import copy
import datetime
import math
import random
from collections import defaultdict
from typing import Any, Iterable

from arcade.shape_list import Shape, ShapeElementList
from sortedcontainers import SortedSet

from core.service.coordinates import Coordinates
from core.service.object import Object, ProjectionObject
from simulator.base import Base, BaseProjection
from simulator.creature import Creature, CreatureProjection
from simulator.tile import Tile, TileProjection
from simulator.world_object import WorldObject


type Tiles2 = dict[int, dict[int, Tile]]
type Tiles3 = dict[int, dict[int, [dict[int, Tile]]]]


class Map(ProjectionObject):
    def __init__(self, width: int, height: int) -> None:
        super().__init__()

        # соотносится с центром окна
        self.center_x = width // 2
        self.center_y = height // 2
        self.offset_x = self.center_x
        self.offset_y = self.center_y

        # множитель размера отображения мира
        self.coeff: float | None = None
        self.min_coeff = 1
        self.max_coeff = 100
        # возвышение, в градусах
        self.elevation: float | None = None
        self.tilt_coeff: float | None = None
        self.min_elevation = 30
        self.max_elevation = 90
        # поворот, в градусах
        self.rotation: float | None = None
        self.center_on_window(width, height)

        self.bases = set[BaseProjection]()
        self.creatures = set[CreatureProjection]()
        self.tiles = set[TileProjection]()
        self.base_polygons = ShapeElementList()
        self.creature_polygons = ShapeElementList()
        self.tile_borders = ShapeElementList()

        self.selected_tiles = set[TileProjection]()

    def init(self) -> Any:
        self.init_tiles()
        self.init_bases()
        self.init_creatures()
        self.inited = True

    @staticmethod
    def init_specific(projections: set[ProjectionObject], shapes: ShapeElementList[Shape], *args) -> None:
        shapes.clear()
        for projection in projections:
            if not projection.inited:
                projection.init(*args)
            shapes.append(projection.shape)

    def init_bases(self) -> None:
        self.init_specific(self.bases, self.base_polygons)

    def init_creatures(self) -> None:
        self.init_specific(self.creatures, self.creature_polygons)

    def init_tiles(self) -> None:
        self.init_specific(self.tiles, self.tile_borders, self.offset_x, self.offset_y, self.coeff, self.tilt_coeff)

    def reset(self) -> None:
        self.reset_creatures()
        self.reset_bases()
        self.reset_tiles()

    def reset_specific(self, projections: set[ProjectionObject], shapes: ShapeElementList[Shape]) -> None:
        for projection in projections:
            projection.inited = False
        shapes.clear()
        self.inited = False

    def reset_bases(self) -> None:
        self.reset_specific(self.bases, self.base_polygons)

    def reset_creatures(self) -> None:
        self.reset_specific(self.creatures, self.creature_polygons)

    def reset_tiles(self) -> None:
        self.reset_specific(self.tiles, self.tile_borders)

    def start(
            self,
            creatures: Iterable[CreatureProjection],
            bases: Iterable[BaseProjection],
            tiles: Iterable[TileProjection]
    ) -> None:
        for projection in bases:
            self.bases.add(projection)
        for projection in creatures:
            self.creatures.add(projection)
        for projection in tiles:
            self.tiles.add(projection)

    def on_draw(self, draw_creatures: bool, draw_bases: bool, draw_tiles: bool) -> None:
        if not self.inited:
            self.init()

        if draw_bases:
            self.base_polygons.draw()
            self.reset_bases()
        if draw_creatures:
            self.creature_polygons.draw()
            self.reset_creatures()
        if draw_tiles:
            self.tile_borders.draw()

    def change_coeff(self, position_x: int, position_y: int, offset: int) -> None:
        scroll_coeff = 10
        coeff_offset = offset * self.coeff / self.max_coeff * scroll_coeff
        old_coeff = self.coeff
        self.coeff = max(min(self.coeff + coeff_offset, self.max_coeff), self.min_coeff)

        if (coeff_diff := self.coeff - old_coeff) != 0:
            move_coeff = -(1 - self.coeff / old_coeff)
            if abs(coeff_diff - coeff_offset) < 0.01:
                move_coeff = round(move_coeff, 1)
            offset_x = (self.offset_x - position_x) * move_coeff
            offset_y = (self.offset_y - position_y) * move_coeff
            self.offset_x += offset_x
            self.offset_y += offset_y

        self.reset()

    def center_on_window(self, width: float, height: float) -> None:
        # todo: вызов данного метода должен перерисовывать карту так, чтобы она целиком помещалась на экране
        self.coeff = 10
        self.elevation = 90
        self.tilt_coeff = 1
        self.rotation = 0

    def change_offset(self, offset_x: int, offset_y: int) -> None:
        self.offset_x += offset_x
        self.offset_y += offset_y
        self.reset()

    def change_tilt(self, offset: int) -> None:
        coeff = 1 / 2
        self.elevation = max(min(self.elevation + offset * coeff, self.max_elevation), self.min_elevation)
        self.tilt_coeff = math.sin(math.radians(self.elevation))
        self.reset()

    def change_rotation(self, offset: int) -> None:
        max_rotation = 360
        self.rotation = (max_rotation + self.rotation + offset) % max_rotation
        self.reset()

    def point_to_coordinates(self, point_x: float, point_y: float) -> Coordinates:
        sqrt = math.sqrt(3)

        radius = self.coeff / 2
        relative_x = point_x - self.offset_x
        relative_y = point_y - self.offset_y
        position_x = round((relative_x * sqrt / 3 - relative_y / 3) / radius)
        position_y = round((relative_y * 2 / 3) / radius / self.tilt_coeff)

        return Coordinates(position_x, position_y)


class World(Object):
    def __init__(
            self,
            radius: int,
            population: int,
            bases_number: int,
            map_width: int,
            map_height: int,
            seed: int = None
    ) -> None:
        super().__init__()

        if seed is None:
            seed = datetime.datetime.now().timestamp()
        self.seed = seed
        self.population = population
        self.bases_number = bases_number
        random.seed(self.seed)

        self.age = 0
        self.center_x = 0
        self.center_y = 0
        # в тайлах
        self.radius = radius

        self.creatures = SortedSet[Creature]()
        self.bases = SortedSet[Base]()
        self.tiles_2: Tiles2 = defaultdict(dict)
        self.tiles_3: Tiles3 = defaultdict(lambda: defaultdict(dict))
        self.tile_set = set[Tile]()
        self.map = Map(map_width, map_height)
        self.prepare()

    def start(self) -> None:
        safe_radius = max(Base.radius, Creature.radius)
        tiles = copy.copy(self.tile_set)

        def init(amount: int, object_class: type[WorldObject], objects_set: SortedSet[WorldObject], *args) -> None:
            for _ in range(amount):
                center_tile = random.choice(list(tiles))
                world_object = object_class(center_tile, *args)

                object_tiles = set()
                object_tiles.add(world_object.center_tile)
                object_tiles = world_object.append_layers(object_tiles, world_object.radius)
                world_object.init(object_tiles)
                object_tiles = world_object.append_layers(world_object.tiles, safe_radius)

                tiles.difference_update(object_tiles)
                objects_set.add(world_object)

        init(self.bases_number, Base, self.bases)
        bases = list(self.bases)
        init(self.population, Creature, self.creatures, bases)

    def stop(self) -> None:
        for creature in self.creatures:
            creature.stop()
        for base in self.bases:
            base.stop()
        self.creatures.clear()
        self.bases.clear()

    def on_update(self) -> None:
        for base in self.bases:
            base.on_update()
        for creature in self.creatures:
            creature.on_update()
        self.age += 1

    # https://www.redblobgames.com/grids/hexagons/#map-storage
    # todo: добавить сохранение/кэширование карты и соседей для более быстрой загрузки
    def prepare(self) -> None:
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                coordinates = Coordinates(x, y)
                if coordinates.in_radius(self.radius + 1):
                    self.add_tile(coordinates)

        for tile in self.tile_set:
            tile.init(self.tiles_2, self.radius)

    def add_tile(self, coordinates: Coordinates) -> None:
        tile = Tile(coordinates)
        self.tiles_2[tile.x][tile.y] = tile
        self.tiles_3[tile.a][tile.b][tile.c] = tile
        self.tile_set.add(tile)
