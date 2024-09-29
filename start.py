import gc
from typing import TextIO

import arcade

from simulator.creature import Creature
from simulator.window import Window
from simulator.world import World


def simulate() -> None:
    window_width = 800
    window_height = 600

    window = Window(window_width, window_height)
    try:
        window.start()
        arcade.run()
        window.stop()
    except Exception as error:
        window.stop()
        raise error
    finally:
        print(f"Симуляция окончена. Возраст мира: {window.world.age}")


if __name__ == "__main__":
    simulate()
