import datetime
import random
from collections import defaultdict
from typing import Any, Iterable

import arcade
from arcade import SpriteList

from core.service.object import Object, ProjectionObject
from simulator.base import Base, BaseSprite
from simulator.creature import Creature, CreatureSprite
from simulator.tile import Tile, TileProjection


class Map(ProjectionObject):
    # множитель размера отображения мира
    coeff: float
    # наклон, в градусах
    tilt: float
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

        self.creature_sprites = SpriteList[CreatureSprite]()
        self.base_sprites = SpriteList[BaseSprite]()
        self.tile_projections = set[TileProjection]()
        # todo: convert borders to background?
        self.tile_borders = arcade.shape_list.ShapeElementList()

    def init(self) -> Any:
        for sprite in self.creature_sprites:
            if not sprite.inited:
                sprite.init()
        for sprite in self.base_sprites:
            if not sprite.inited:
                sprite.init()
        for projection in self.tile_projections:
            if not projection.inited:
                projection.init(self.offset_x, self.offset_y, self.coeff, self.tilt)
                self.tile_borders.append(projection.border)

        self.inited = True

    def prepare(
            self,
            creatures_sprites: Iterable[CreatureSprite],
            bases_sprites: Iterable[BaseSprite],
            tiles_projections: Iterable[TileProjection]
    ) -> None:
        for sprite in creatures_sprites:
            self.creature_sprites.append(sprite)
        for sprite in bases_sprites:
            self.base_sprites.append(sprite)
        for projection in tiles_projections:
            self.tile_projections.add(projection)
            if projection.inited:
                self.tile_borders.append(projection.border)

    def reset(self) -> None:
        for sprite in self.creature_sprites:
            sprite.inited = False
        for sprite in self.base_sprites:
            sprite.inited = False
        for projection in self.tile_projections:
            projection.inited = False
        self.tile_borders.clear()
        self.inited = False

    def on_draw(self, draw_creatures: bool, draw_bases: bool, draw_tiles: bool) -> None:
        if not self.inited:
            self.init()

        if draw_creatures:
            self.creature_sprites.draw()
        if draw_bases:
            self.base_sprites.draw()
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
        self.rotation = 0

    def change_offset(self, offset_x: int, offset_y: int) -> None:
        self.offset_x += offset_x
        self.offset_y += offset_y
        self.reset()

    def change_tilt(self, offset: int) -> None:
        tilt_coeff = 1 / 2
        self.tilt = max(min(self.tilt + offset * tilt_coeff, self.max_tilt), self.min_tilt)
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
        self.map = Map(map_width, map_height)
        self.prepare()

        creature_sprites = (x.sprite for x in self.creatures)
        bases_sprites = (x.sprite for x in self.bases)
        tiles_projections = (y.projection for x in self.tiles.values() for y in x.values())
        self.map.prepare(creature_sprites, bases_sprites, tiles_projections)

    def start(self) -> None:
        for _ in range(self.population):
            # todo: get to creatures random free tiles?
            creature = Creature(0, 0)
            self.creatures.add(creature)
            self.tiles[creature.position_x][creature.position_y].object = creature
            creature.start()
        for _ in range(self.bases_amount):
            # todo: get to bases random free tiles?
            base = Base(0, 0)
            self.bases.add(base)
            self.tiles[base.position_x][base.position_y].object = base
            base.start()

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
                    self.tiles[x][y] = Tile(x, y)
