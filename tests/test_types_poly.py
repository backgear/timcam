from timcam.types.poly import Loop, Jumble
from timcam.types.point import Point


def test_winding():
    p = Loop([Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)])
    # inside
    assert p.winding_of(Point(5, 5)) == 1
    assert Point(5, 5) in p
    # outside
    assert p.winding_of(Point(15, 5)) == 0
    # on boundary
    assert p.winding_of(Point(0, 0)) == 1

    assert p.direction() > 0

    p2 = Loop(p.points[::-1])
    assert p2.direction() < 0


def test_jumble():
    j = Jumble()
    j.add_line(Point(0, 0), Point(10, 0))
    j.add_line(Point(5, 5), Point(0, 0))
    j.add_line(Point(10, 0), Point(5, 5))
    j.close_loops()
    assert len(j.full_loops) == 1
