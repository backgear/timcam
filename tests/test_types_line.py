from timcam.types.line import VariableWidthPolyline
from timcam.types.point import Point


def test_variable_width_polyline():
    t = VariableWidthPolyline(Point(0, 0), 0)
    t.add_point(Point(5, 0), 5)
    t.add_point(Point(9, 0), 9)
    result = list(t.iter_width_along(2))
    assert result == [
        (Point(0.0, 0.0), 0.0),
        (Point(2.0, 0.0), 2.0),
        (Point(4.0, 0.0), 4.0),
        (Point(6.0, 0.0), 6.0),
        (Point(8.0, 0.0), 8.0),
        (Point(9.0, 0.0), 9.0),  # last segment shorter
    ]


def test_variable_width_polyline_remainder_along_line():
    t = VariableWidthPolyline(Point(0, 0), 0)
    t.add_point(Point(5, 0), 5)
    t.add_point(Point(5, 4), 9)
    result = list(t.iter_width_along(2))
    assert result == [
        (Point(0.0, 0.0), 0.0),
        (Point(2.0, 0.0), 2.0),
        (Point(4.0, 0.0), 4.0),
        (Point(5.0, 1.0), 6.0),  # not euclidean distance, it's along the line
        (Point(5.0, 3.0), 8.0),
        (Point(5.0, 4.0), 9.0),  # last segment shorter
    ]
