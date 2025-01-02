from math import pi as PI
from timcam.types.point import Point


def test_repr():
    pt = Point(1, -1)
    assert repr(pt) == "Point(1, -1)"


def test_angle():
    pt = Point.from_angle(PI / 6)
    assert pt == Point(0.8660254037844387, 0.5)
    assert pt.to_angle() == PI / 6


def test_perpendicular():
    pt = Point.from_angle(PI / 6)
    assert pt.perpendicular(True) == Point.from_angle(PI / 6 - PI / 2)
    assert pt.perpendicular(False) == Point.from_angle(PI / 6 + PI / 2)
    assert pt.perpendicular(True).perpendicular(False) == pt
    # Three rights make a left
    assert pt.perpendicular(True).perpendicular(True).perpendicular(
        True
    ) == pt.perpendicular(False)
    assert (
        pt.perpendicular(True)
        .perpendicular(True)
        .perpendicular(True)
        .perpendicular(True)
        == pt
    )
