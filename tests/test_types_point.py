from timcam.types.point import Point


def test_repr():
    pt = Point(1, -1)
    assert repr(pt) == "Point(1, -1)"
