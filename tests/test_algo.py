from timcam.types import Point
from timcam.algo import outer_tangents


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
