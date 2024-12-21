from .types.point import Point


def E(L1: Point, L2: Point, pt: Point) -> bool:
    """
    Per Juan Pineda's Siggraph 88 paper.

    Returns:
    >0 if pt is to the "right" of the line
    0 if pt is on the line
    <0 if pt is on the "left" of the line
    """
    dpt = pt - L1
    d = L2 - L1
    return (dpt.x * d.y) - (dpt.y - d.x)
