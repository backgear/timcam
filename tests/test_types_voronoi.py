from timcam.types import Voronoi, Loop, Poly, Point


def test_smoke():
    l = Loop(
        points=[
            Point(0, 0),
            Point(10, 0),
            Point(10, 5),
            Point(0, 5),
        ]
    )
    v = Voronoi(Poly(l, []))
    dag = v.dag()

    assert dag.start_rad == 2.5
    assert dag.start_pt == Point(7.5, 2.5)
    assert len(dag.next) == 3

    # These verify that we sorted by path length, then y
    assert dag.next[0].end_pt == Point(10, 5)
    assert dag.next[0].end_rad == 0.0

    assert dag.next[1].end_pt == Point(10, 0)
    assert dag.next[1].end_rad == 0.0

    assert dag.next[2].end_pt == Point(2.5, 2.5)
    assert dag.next[2].end_rad == 2.5

    assert len(dag.next[2].next) == 2

    # The are sorted by y, same length
    assert dag.next[2].next[0].end_pt == Point(0, 5)
    assert dag.next[2].next[0].end_rad == 0

    assert dag.next[2].next[1].end_pt == Point(0, 0)
    assert dag.next[2].next[1].end_rad == 0.0


def test_smoke_mountain():
    # This shape is also available in tests/shapes/07_mountain.dxf
    l = Loop(
        points=[
            Point(0, 0),
            Point(20, 0),
            Point(16, 8),
            Point(10, 5),
            Point(3, 10),
        ]
    )
    v = Voronoi(Poly(l, []))
    dag = v.dag()

    assert dag.start_rad == 3.80782088862309
    assert dag.start_pt == Point(5.117827987412649, 3.807820888623091)

    assert len(dag.next) == 3

    # These verify that we shorted by path length, then y
    assert dag.next[0].end_pt == Point(0, 0)
    assert dag.next[0].end_rad == 0.0

    assert dag.next[1].end_pt == Point(3, 10)
    assert dag.next[1].end_rad == 0.0

    assert dag.next[2].end_pt == Point(8.397674732957373, 2.7567446261403226)
    assert dag.next[2].end_rad == 2.7567446261403217

    assert len(dag.next[2].next) == 1
