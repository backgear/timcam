from __future__ import annotations

import pyvoronoi

from dataclasses import dataclass
from typing import Optional

from .point import Point


@dataclass
class VariableWidthPolylinePoint:
    point: Point
    radius: float
    length: Optional[float]


class Polyline:
    def __init__(self, points):
        self.points = points

    def iter_along(self, stepover):
        """
        yields `stepover`-spaced points, with ill-defined corner behavior
        """
        it = iter(self.points)
        prev = next(it)
        pt = None
        for t in it:
            unit = (t - prev).norm()
            while (t - prev).length() > stepover:
                prev += unit * stepover
                yield prev
            pt = t
        yield pt

    def __repr__(self):
        return "%s(points=%s)" % (self.__class__.__name__, self.points)


class VariableWidthPolyline:
    """
    Stores information about a polyline that varies in width along its length.

    This makes the most sense as a discretized approximation of a mathematical
    curve, where the angle at each vertex is quite small.  The functions use the
    term "radius" for "half width" because that's the inscribed circle found
    through the voronoi diagram in voronoi.py that can construct this class
    during traversal.
    """

    def __init__(self, starting_point, starting_radius):
        self.ptr: list[VariableWidthPolylinePoint] = [
            VariableWidthPolylinePoint(starting_point, starting_radius, None),
        ]

    def add_point(self, new_point, new_radius):
        """Suitable only for already-discretized lines, not parabola or arc"""
        length = pyvoronoi.Distance(new_point, self.ptr[-1].point)
        self.ptr.append(VariableWidthPolylinePoint(new_point, new_radius, length))

    def iter_width_along(self, stepover: float):
        """
        yields `stepover`-spaced points [except the final one, which may be
        shorter] along with the appropriate radius at each.  All points will
        exist on the line, and the radius will be appropriate for that point.
        No need to keep track of min in a span yourself.

        The length for all except the last one should be exactly `stepover`.
        """
        it = iter(self.ptr)
        prev = next(it)
        remainder = 0.0

        yield prev.point, prev.radius

        for each in it:
            assert remainder < stepover

            length = each.length
            left = length
            unit = (each.point - prev.point).norm()
            pt = prev.point
            dr = prev.radius - each.radius  # this is "backwards" on purpose

            while (remainder + left) >= stepover:
                pt += unit * (stepover - remainder)
                left -= stepover - remainder
                r = (left / length) * dr + each.radius
                yield (pt, r)
                remainder = 0.0
            remainder = left
            prev = each

        if remainder:
            yield (each.point, each.radius)
