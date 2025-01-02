from math import pi as PI

from timcam.types import Point
from timcam.algo import outer_tangents, outer_tangent_angles


def test_outer_tangents_parallel():
    c1 = Point(0, 0)
    c2 = Point(5, 0)

    (a, b), (c, d) = outer_tangents(c1, 3, c2, 3)
    assert a == Point(0, 3)
    assert b == Point(5, 3)

    assert c == Point(0, -3)
    assert d == Point(5, -3)


def test_outer_tangents_reverse_parallel():
    c1 = Point(5, 0)
    c2 = Point(0, 0)

    (a, b), (c, d) = outer_tangents(c1, 3, c2, 3)
    assert a == Point(5, -3)
    assert b == Point(0, -3)

    assert c == Point(5, 3)
    assert d == Point(0, 3)


def test_outer_tangents_345():
    c1 = Point(0, 0)
    c2 = Point(5, 0)

    (a, b), (c, d) = outer_tangents(c1, 0, c2, 3)
    assert a == Point(0, 0)
    assert b == Point(3.2, 2.4)

    assert c == Point(0, 0)
    assert d == Point(3.2, -2.4)


def test_outer_tangents_other_345():
    c1 = Point(0, 0)
    c2 = Point(5, 0)

    (a, b), (c, d) = outer_tangents(c1, 3, c2, 0)
    assert a == Point(1.8, 2.4)
    assert b == Point(5, 0)

    assert c == Point(1.8, -2.4)
    assert d == Point(5, 0)


def test_outer_tangent_angles():
    c1 = Point(0, 0)
    c2 = Point(1.4142135623730951, 0)
    rv = outer_tangent_angles(c1, 0, c2, 1)
    assert rv is not None
    assert rv[0] == 0  # theta
    assert rv[1] == PI * 3 / 4  # phi, isosocles (angle measured from c2)
