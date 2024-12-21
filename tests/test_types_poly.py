from timcam.types.poly import Loop
from timcam.types.point import Point

def test_winding():
    p = Loop([Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)])
    # inside
    assert p.winding_of(Point(5, 5)) == -1
    assert Point(5, 5) in p
    # outside
    assert p.winding_of(Point(15, 5)) == 0
    # on boundary
    assert p.winding_of(Point(0, 0)) == 0

    assert p.direction() > 0

    p2 = Loop(p.points[::-1])
    assert p2.direction() < 0
