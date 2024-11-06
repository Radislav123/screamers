import datetime
import random
from collections import defaultdict
from typing import Iterable

import arcade
from arcade import SpriteList

from core.service.object import Object
from simulator.base import Base, BaseSprite
from simulator.creature import Creature, CreatureSprite
from simulator.tile import Tile, TileProjection


class Map(Object):
    def __init__(self, center_x: int, center_y: int) -> None:
        super().__init__()

        # соотносится с центром окна
        self.center_x = center_x
        self.center_y = center_y
        # множитель размера отображения мира
        self.coeff = 50
        self.creatures_sprites = SpriteList[CreatureSprite]()
        self.bases_sprites = SpriteList[BaseSprite]()
        # todo: convert borders to background?
        self.tiles_borders = arcade.shape_list.ShapeElementList()

    def prepare(
            self,
            creatures_sprites: Iterable[CreatureSprite],
            bases_sprites: Iterable[BaseSprite],
            tiles_projections: Iterable[TileProjection]
    ) -> None:
        for sprite in creatures_sprites:
            self.creatures_sprites.append(sprite)
        for sprite in bases_sprites:
            self.bases_sprites.append(sprite)
        for projection in tiles_projections:
            self.tiles_borders.append(projection.border)


class World(Object):
    def __init__(
            self,
            radius: int,
            population: int,
            bases_amount: int,
            center_x: int,
            center_y: int,
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

        self.creatures: dict[int, Creature] = {}
        self.bases: dict[int, Base] = {}
        self.tiles: dict[int, dict[int, Creature | Base | Tile]] = defaultdict(dict)
        self.map = Map(center_x, center_y)
        self.prepare()

        creature_sprites = (x.sprite for x in self.creatures.values())
        bases_sprites = (x.sprite for x in self.bases.values())
        tiles_projections = (y.projection for x in self.tiles.values() for y in x.values())
        self.map.prepare(creature_sprites, bases_sprites, tiles_projections)

    def start(self) -> None:
        for _ in range(self.population):
            # todo: get to creatures random free tiles?
            creature = Creature(0, 0)
            self.creatures[creature.id] = creature
            self.tiles[creature.position_x][creature.position_y] = creature
            creature.start()
        for _ in range(self.bases_amount):
            # todo: get to bases random free tiles?
            base = Base(0, 0)
            self.bases[base.id] = base
            self.tiles[base.position_x][base.position_y] = base
            base.start()

    def stop(self) -> None:
        for creature in self.creatures.values():
            creature.stop()
        for base in self.bases.values():
            base.stop()
        self.creatures.clear()
        self.bases.clear()

    def on_update(self) -> None:
        for creature in self.creatures.values():
            creature.on_update()
        for base in self.bases.values():
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
                    self.tiles[x][y] = Tile(x, y, self.map.center_x, self.map.center_y, self.map.coeff)
