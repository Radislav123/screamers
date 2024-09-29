import datetime
import random
from enum import Enum
from typing import Iterable

from arcade import SpriteList
from pyglet.math import Vec2

from core.service.object import Object
from simulator.creature import Creature, CreatureSprite

from simulator.base import Base, BaseSprite


class Region:
    pass


class Tile(Enum):
    Free = 0
    Border = 1


class Map(Object):
    def __init__(
            self,
            center: Vec2,
            creatures_sprites: Iterable[CreatureSprite],
            bases_sprites: Iterable[BaseSprite]
    ) -> None:
        # соотносится с центром окна
        self.center = center
        self.creatures_sprites = SpriteList[CreatureSprite]()
        for sprite in creatures_sprites:
            self.creatures_sprites.append(sprite)
        self.bases_sprites = SpriteList[BaseSprite]()
        for sprite in bases_sprites:
            self.bases_sprites.append(sprite)
        # todo: write it
        # todo: convert border sprites to 1 sprite or background?
        self.border_sprites = SpriteList(True)


class World(Object):
    def __init__(self, radius: int, population: int, bases_amount: int, center: Vec2, seed: int = None) -> None:
        if seed is None:
            seed = datetime.datetime.now().timestamp()
        self.seed = seed
        self.population = population
        self.bases_amount = bases_amount
        random.seed(self.seed)

        self.age = 0
        self.center = Vec2(0, 0)
        # в тайлах
        self.radius = radius
        self.point_to_region: dict[Vec2, Region] = {}

        self.creatures: dict[int, Creature] = {}
        self.bases: dict[int, Base] = {}
        self.tiles: dict[Vec2, Creature | Tile] = {}
        self.prepare()

        self.map = Map(center, (x.sprite for x in self.creatures.values()), (x.sprite for x in self.bases.values()))

    def start(self) -> None:
        for _ in range(self.population):
            # todo: get creatures random free tiles
            creature = Creature(Vec2(0, 0))
            self.creatures[creature.id] = creature
            self.tiles[creature.position] = creature
            creature.start()

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
        lower_border = self.radius - 1
        upper_border = self.radius * 2 - 1
        for x in range(upper_border):
            for y in range(upper_border):
                x_y = x + y
                if lower_border < x_y < upper_border:
                    self.tiles[Vec2(x, y)] = Tile.Free
                elif x_y == lower_border or x_y == upper_border:
                    self.tiles[Vec2(x, y)] = Tile.Border
