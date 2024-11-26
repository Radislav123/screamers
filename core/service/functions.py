from itertools import count, takewhile
from typing import Iterator


def float_range(start: float, stop: float, step: float) -> Iterator[float]:
    return takewhile(lambda x: x < stop, count(start, step))
