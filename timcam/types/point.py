from __future__ import annotations

from typing import Any


class Point:
    """
    Simple 2D point class with integer coordinates
    """

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: Any) -> Point:
        if not isinstance(other, Point):
            other = Point(other)
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Any) -> Point:
        if not isinstance(other, Point):
            other = Point(other)
        return self.__class__(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return "%s(%s, %s)" % (self.__class__.__name__, self.x, self.y)

    @classmethod
    def from_dxf_vec(cls, vec, scale_factor) -> Point:
        # TODO int(round(...))?
        return cls(int(vec.x * scale_factor), int(vec.y * scale_factor))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self):
        return 2

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError(i)
