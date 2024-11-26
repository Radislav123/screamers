import functools
import math
from typing import Self

import PIL.Image
import arcade
from PIL import Image
from arcade import Texture as ArcadeTexture, color
from arcade.types import Color

from core.service.figure import Circle, ClosedFigure, Hexagon, RoundedRectangle


class Texture(ArcadeTexture):
    from_texture_counter = 0

    @classmethod
    def from_texture(cls, texture: arcade.Texture, cache_name: str = None) -> Self:
        if cache_name is None:
            cache_name = str(cls.from_texture_counter)

        cls.from_texture_counter += 1
        return cls(
            texture.image.copy(),
            hit_box_algorithm = texture.hit_box_algorithm,
            hit_box_points = texture.hit_box_points,
            hash = cache_name
        )

    @staticmethod
    @functools.cache
    def get_figure(figure_class: type[ClosedFigure], *args, **kwargs) -> ClosedFigure:
        return figure_class(*args, **kwargs)

    @classmethod
    @functools.cache
    def create_rounded_rectangle(
            cls,
            size: tuple[int | float, int | float] = (100, 50),
            rounding_radius: int = None,
            # в пикселях
            border_thickness: int = 2,
            main_color: Color = color.WHITE,
            border_color: Color = color.BLACK,
            background_color: Color = color.TRANSPARENT_BLACK,
            transparent_background: bool = True
    ) -> Self:
        if rounding_radius is None:
            rounding_radius = min(size) // 10
        figure = cls.get_figure(RoundedRectangle, rounding_radius, size[0], size[1], size[0] / 2, size[1] / 2)

        reduce = 2 * border_thickness
        inner_size = (size[0] - reduce, size[1] - reduce)
        inner_figure = cls.get_figure(
            RoundedRectangle,
            rounding_radius,
            inner_size[0],
            inner_size[1],
            size[0] / 2,
            size[1] / 2
        )

        # noinspection PyTypeChecker
        texture = cls.create_with_figure(
            figure,
            inner_figure,
            size,
            main_color,
            border_color,
            background_color,
            transparent_background
        )
        return texture

    @classmethod
    @functools.cache
    def create_circle(
            cls,
            radius: int | float = 25,
            # в пикселях
            border_thickness: int = 3,
            main_color: Color = color.WHITE,
            border_color: Color = color.BLACK,
            background_color: Color = color.TRANSPARENT_BLACK,
            transparent_background: bool = True
    ) -> Self:
        figure = cls.get_figure(Circle, radius, radius, radius)
        inner_radius = radius - border_thickness
        inner_figure = cls.get_figure(Circle, inner_radius, radius, radius)

        # noinspection PyTypeChecker
        texture = cls.create_with_figure(
            figure,
            inner_figure,
            (radius * 2, radius * 2),
            main_color,
            border_color,
            background_color,
            transparent_background
        )
        return texture

    @classmethod
    @functools.cache
    def create_hexagon(
            cls,
            radius: int | float = 25,
            # в пикселях
            border_thickness: int = 3,
            main_color: Color = color.WHITE,
            border_color: Color = color.BLACK,
            background_color: Color = color.TRANSPARENT_BLACK,
            transparent_background: bool = True
    ) -> Self:
        width = math.sqrt(3) * radius
        height = 2 * radius
        figure = cls.get_figure(Hexagon, radius, width / 2, height / 2)
        inner_radius = radius - border_thickness
        inner_figure = cls.get_figure(Hexagon, inner_radius, width / 2, height / 2)

        # noinspection PyTypeChecker
        texture = cls.create_with_figure(
            figure,
            inner_figure,
            (figure.width, figure.height),
            main_color,
            border_color,
            background_color,
            transparent_background
        )
        return texture

    @classmethod
    @functools.cache
    def create_with_figure(
            cls,
            figure: ClosedFigure,
            inner_figure: ClosedFigure,
            size: tuple[int | float, int | float] = (100, 50),
            main_color: Color = color.WHITE,
            border_color: Color = color.BLACK,
            background_color: Color = color.TRANSPARENT_BLACK,
            transparent_background: bool = True
    ) -> Self:
        size = list(size)
        for dimension in range(len(size)):
            if isinstance(size[dimension], float):
                # noinspection PyUnresolvedReferences
                size[dimension] = int(size[dimension]) + (size[dimension] % 1 > 0)
        image = Image.new("RGBA", size, main_color)

        # обрезание прямоугольника до необходимой фигуры
        alpha = Image.new("L", size, 0)
        for x in range(size[0]):
            for y in range(size[1]):
                if figure.belongs(x, y):
                    alpha.putpixel((x, y), image.getpixel((x, y))[3])
        image.putalpha(alpha)

        # наложение границы
        if main_color != border_color:
            colored = Image.new("RGBA", size, border_color)
            border_mask = Image.new("L", size, 0)

            for x in range(size[0]):
                for y in range(size[1]):
                    if inner_figure.belongs(x, y):
                        border_mask.putpixel((x, y), 255)
            colored.putalpha(alpha)
            image = Image.composite(image, colored, border_mask)

        if not transparent_background and (background_color != main_color or background_color != border_color):
            background = Image.new("RGBA", size, background_color)
            image = Image.composite(image, background, image.getchannel(3))

        return Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)

    def with_image(self, image: PIL.Image.Image, maintain_ratio: bool = True, center: bool = True) -> Self:
        if maintain_ratio:
            image.thumbnail(self.image.size)
            if center:
                left = int(self.image.width / 2 - image.width / 2)
                self.image.alpha_composite(image, (left, 0))
            else:
                self.image.alpha_composite(image)
        else:
            image = image.resize(self.image.size)
            self.image.alpha_composite(image)

        return self
