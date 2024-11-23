from typing import Any, Self

from arcade.shape_list import Shape

from core.service import settings
from core.service.logger import Logger
from core.service.settings import Settings


class ThirdPartyMixin:
    settings = Settings()
    logger = Logger(__qualname__)


class Object:
    settings = settings.Settings()
    counter = 0
    logger = Logger(__qualname__)

    def __init__(self) -> None:
        super().__init__()
        self.id = self.counter
        self.__class__.counter += 1

    def __lt__(self, other: "Self") -> bool:
        return self.id < other.id

    def init(self, *args, **kwargs) -> Any:
        pass

    def start(self, *args, **kwargs) -> Any:
        pass

    def stop(self, *args, **kwargs) -> Any:
        pass


class ProjectionObject(Object):
    def __init__(self) -> None:
        super().__init__()
        self.inited = False
        self.shape: Shape | None = None

    def on_draw(self, *args, **kwargs) -> Any:
        pass


class PhysicalObject(Object):
    def on_update(self, *args, **kwargs) -> Any:
        pass
