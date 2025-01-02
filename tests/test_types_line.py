from math import pi as PI
from timcam.types.line import (
    VariableWidthPolyline,
    IterWidthPoint,
    VariableWidthPolylinePoint,
)
from timcam.types.point import Point


def test_variable_width_polyline():
    t = VariableWidthPolyline(Point(0, 0), 0.1)
    t.add_point(Point(5, 0), 2)
    assert t.ptr[0] == VariableWidthPolylinePoint(
        Point(0, 0),
        0.1,
        None,
        None,
        None,
    )
    assert t.ptr[1] == VariableWidthPolylinePoint(
        Point(5, 0),
        2.0,
        5.0,
        0.0,
        1.9605926232691573,
    )

    result = list(t.iter_width_along(2))
    assert result[0] == IterWidthPoint(Point(0.0, 0.0), 0.1, None, None, None, None)
    assert result[1] == IterWidthPoint(
        Point(2.0, 0.0),
        0.8600000000000001,
        0.0,
        1.9605926232691573,
        Point(1.6731999999999998, 0.7954883782934858),
        Point(1.6731999999999998, -0.7954883782934858),
    )
    #     (Point(4.0, 0.0), 4.0),
    #     (Point(6.0, 0.0), 6.0),
    #     (Point(8.0, 0.0), 8.0),
    #     (Point(9.0, 0.0), 9.0),  # last segment shorter
    # ]


# def test_variable_width_polyline_remainder_along_line():
#     t = VariableWidthPolyline(Point(0, 0), 0)
#     t.add_point(Point(5, 0), 5)
#     t.add_point(Point(5, 4), 9)
#     result = list(t.iter_width_along(2))
#     assert result == [
#         IterWidthPoint(Point(0.0, 0.0), 0.0, None, None, None, None),
#         (Point(2.0, 0.0), 2.0),
#         (Point(4.0, 0.0), 4.0),
#         (Point(5.0, 1.0), 6.0),  # not euclidean distance, it's along the line
#         (Point(5.0, 3.0), 8.0),
#         (Point(5.0, 4.0), 9.0),  # last segment shorter
#     ]
