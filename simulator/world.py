import copy
import datetime
import math
import random
from collections import defaultdict
from typing import Any, Iterable

import arcade

from core.service.object import Object, ProjectionObject
from simulator.base import Base, BaseSprite
from simulator.creature import Creature, CreatureSprite
from simulator.tile import Tile, TileProjection


class Map(ProjectionObject):
    # множитель размера отображения мира
    coeff: float
    # наклон, в градусах
    tilt: float
    tilt_coeff: float
    # поворот, в градусах
    rotation: float

    def __init__(self, width: int, height: int) -> None:
        super().__init__()

        # соотносится с центром окна
        self.center_x = width // 2
        self.center_y = height // 2
        self.offset_x = self.center_x
        self.offset_y = self.center_y

        self.center_on_window(width, height)
        self.min_coeff = 1
        self.max_coeff = 100
        self.min_tilt = 45
        self.max_tilt = 90

        self.bases = set[BaseSprite]()
        self.creatures = set[CreatureSprite]()
        self.tiles = set[TileProjection]()
        self.base_polygons = arcade.shape_list.ShapeElementList()
        self.creature_polygons = arcade.shape_list.ShapeElementList()
        self.tile_borders = arcade.shape_list.ShapeElementList()

    def init(self) -> Any:
        for projection in self.tiles:
            if not projection.inited:
                projection.init(self.offset_x, self.offset_y, self.coeff, self.tilt_coeff)
                self.tile_borders.append(projection.border)
        for projection in self.bases:
            if not projection.inited:
                projection.init()
                self.base_polygons.append(projection.polygon)
        for projection in self.creatures:
            if not projection.inited:
                projection.init()
                self.creature_polygons.append(projection.polygon)

        self.inited = True

    def start(
            self,
            creatures: Iterable[CreatureSprite],
            bases: Iterable[BaseSprite],
            tiles: Iterable[TileProjection]
    ) -> None:
        for projection in bases:
            self.bases.add(projection)
        for projection in creatures:
            self.creatures.add(projection)
        for projection in tiles:
            self.tiles.add(projection)
            if projection.inited:
                self.tile_borders.append(projection.border)

    def reset(self) -> None:
        for sprite in self.bases:
            sprite.inited = False
        for sprite in self.creatures:
            sprite.inited = False
        for projection in self.tiles:
            projection.inited = False
        self.base_polygons.clear()
        self.creature_polygons.clear()
        self.tile_borders.clear()
        self.inited = False

    def on_draw(self, draw_creatures: bool, draw_bases: bool, draw_tiles: bool) -> None:
        if not self.inited:
            self.init()

        if draw_bases:
            self.base_polygons.draw()
        if draw_creatures:
            self.creature_polygons.draw()
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
        self.tilt = 90
        self.tilt_coeff = 1
        self.rotation = 0

    def change_offset(self, offset_x: int, offset_y: int) -> None:
        self.offset_x += offset_x
        self.offset_y += offset_y
        self.reset()

    def change_tilt(self, offset: int) -> None:
        coeff = 1 / 2
        self.tilt = max(min(self.tilt + offset * coeff, self.max_tilt), self.min_tilt)
        self.tilt_coeff = math.sin(math.radians(self.tilt))
        self.reset()

    def change_rotation(self, offset: int) -> None:
        max_rotation = 360
        self.rotation = (max_rotation + self.rotation + offset) % max_rotation
        self.reset()


class World(Object):
    def __init__(
            self,
            radius: int,
            population: int,
            bases_amount: int,
            map_width: int,
            map_height: int,
            seed: int = None
    ) -> None:
        super().__init__()

        if seed is None:
            seed = datetime.datetime.now().timestamp()
        self.seed = seed
        self.population = population
        self.bases_amount = bases_amount
        random.seed(self.seed)

        self.age = 0
        self.center_x = 0
        self.center_y = 0
        # в тайлах
        self.radius = radius

        self.creatures = set[Creature]()
        self.bases = set[Base]()
        self.tiles: dict[int, dict[int, Tile]] = defaultdict(dict)
        self.tile_set = set[Tile]()
        self.map = Map(map_width, map_height)
        self.prepare()

    def start(self) -> None:
        tiles = copy.copy(self.tile_set)
        base_tiles = random.sample(list(tiles), self.bases_amount)
        for tile in base_tiles:
            base = Base(0, 0)
            self.bases.add(base)
            tile.object = base
            base.sprite.tile_projection = tile.projection
            base.start()

        bases = list(self.bases)
        tiles.difference_update(base_tiles)
        creature_tiles = random.sample(list(tiles), self.population)
        for tile in creature_tiles:
            creature = Creature(0, 0, bases)
            self.creatures.add(creature)
            tile.object = creature
            creature.sprite.tile_projection = tile.projection
            creature.start()

    def stop(self) -> None:
        for creature in self.creatures:
            creature.stop()
        for base in self.bases:
            base.stop()
        self.creatures.clear()
        self.bases.clear()

    def on_update(self) -> None:
        for creature in self.creatures:
            creature.on_update()
        for base in self.bases:
            base.on_update()

    # https://www.redblobgames.com/grids/hexagons/#map-storage
    def prepare(self) -> None:
        x_start = -self.radius
        x_stop = self.radius
        y_start = -self.radius
        y_stop = self.radius
        for x in range(x_start, x_stop + 1):
            for y in range(y_start, y_stop + 1):
                if abs(x + y) <= self.radius:
                    tile = Tile(x, y)
                    self.tiles[x][y] = tile
                    self.tile_set.add(tile)
