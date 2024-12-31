from __future__ import annotations

from math import cos, sin, acos, atan2, pi as PI

from .types.point import Point


def E(L1: Point, L2: Point, pt: Point) -> bool:
    """
    Per Juan Pineda's Siggraph 88 paper, but with the sign flipped.

    Returns:
    >0 if pt is to the "left" of the line
    0 if pt is on the line
    <0 if pt is on the "right" of the line
    """
    dpt = pt - L1
    d = L2 - L1
    return (d.x * dpt.y) - (dpt.x * d.y)


def outer_tangents(
    c1: Point, r1: float, c2: Point, r2: float
) -> tuple[Point, Point, Point, Point]:
    """
    Calculates the outer tangent lines between two circles.

    Parameters:
    c1: Center of the first circle
    r1: Radius of the first circle
    c2: Center of the second circle
    r2: Radius of the second circle

    Returns:
    ((a, b), (c, d)) points representing the two lines (left and right, from the
    perspectve of the vector c1 -> c2)
    """

    # Calculate the distance between the centers
    d = (c2 - c1).length()

    # Check if the circles intersect or are contained within each other
    # if d < abs(r1 - r2) or d < r1 + r2:
    #     return None

    # Calculate the angle between the centers
    delta = c2 - c1
    theta = atan2(delta.y, delta.x)

    # Calculate the angle to the tangent points
    phi = acos((r1 - r2) / d)

    # Calculate the tangent points for the first circle
    t1_1 = c1 + Point(cos(theta + phi), sin(theta + phi)) * r1
    t1_2 = c1 + Point(cos(theta - phi), sin(theta - phi)) * r1

    # Calculate the tangent points for the second circle
    t2_1 = c2 + Point(cos(theta + phi), sin(theta + phi)) * r2
    t2_2 = c2 + Point(cos(theta - phi), sin(theta - phi)) * r2

    return ((t1_1, t2_1), (t1_2, t2_2))


def pt_line_distance(p, a, b):
    x0, y0 = p
    x1, y1 = a
    x2, y2 = b
    return (
        abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        / ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    )


def angle_similarity(p1, p2):
    """
    angle similarity between two vectors

    The mod/subtract is intended to deal with a discontinuity where PI-e and
    PI+e compare maximally different.
    """
    t = atan2(*p1) - atan2(*p2)
    t %= PI * 2
    if t > PI:
        t -= PI * 2
    return abs(t)


def lines(it):
    """
    Returns pairs of points, assuming the first point isn't duplicated yet.
    """
    t = list(it)
    yield from zip(t, t[1:] + t[:1])
