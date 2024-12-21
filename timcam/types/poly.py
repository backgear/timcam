from __future__ import annotations

from logging import getLogger

from .point import Point
from ..algo import E

from typing import Optional

logger = getLogger(__name__)

EVEN_ODD = 0
POCKET_ALL = 1


def _lines(it):
    t = list(it)
    yield from zip(t, t[1:] + t[:1])


def _min_idx(it):
    m_idx = -1
    m_value = None
    for i, v in enumerate(it):
        if m_value is None or v < m_value:
            m_idx = i
            m_value = v
    return m_idx


class Loop:
    """
    Simple 2D closed polygon class using (integer) Point coordinates.

    Widely assumed by other code to be simple (non-self-intersecting), and in
    the "correct" order, but not necessarily convex.
    """

    __slots__ = ("points",)
    points: list[Point]

    def __init__(self, points=()):
        self.points = list(points)

    def winding_of(self, pt: Point) -> int:
        """
        Find the winding number for this point/loop.

        Returns 0 iif the point is outside.
        """
        count = 0
        for v1, v2 in _lines(self.points):
            if v1.y <= pt.y:
                if v2.y > pt.y:
                    if E(v1, v2, pt) > 0:
                        count += 1
            else:
                if v2.y <= pt.y:
                    if E(v1, v2, pt) < 0:
                        count -= 1
        return count

    def __contains__(self, pt: Point) -> bool:
        return self.winding_of(pt) != 0

    def direction(self) -> int:
        bi = _min_idx(self.points)
        ai = (bi - 1) % len(self.points)
        ci = (bi + 1) % len(self.points)
        a = self.points[ai]
        b = self.points[bi]
        c = self.points[ci]
        # print(b)
        det = (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)
        return det


class Poly:
    outline: Loop
    holes: Optional[list[Loop]] = None

    def __init__(self, outline):
        self.outline = outline
        self.holes = []

    def __repr__(self) -> str:
        return "%s(outline=%d points, holes=%d loops)" % (
            self.__class__.__name__,
            len(self.outline.points),
            len(self.holes),
        )


class Jumble:
    def __init__(self):
        self.partial_loops = []
        self.full_loops: list[Loop] = []

    def add_line(self, pt1, pt2):
        """
        Add one line segment, potentially adding to an existing partial loop.

        Promotion to full loops is done at the end.  Correctness is preserved
        even if segments from multiple loops are interleaved, but it is less
        performant to have lots of partial loops sitting around.
        """
        for p in self.partial_loops:
            if p[-1] == pt1:
                p.append(pt2)
                break
        else:
            self.partial_loops.insert(0, [pt1, pt2])

    def close_loops(self) -> None:
        """
        Well-behaved input has relatively few loops and no duplicated points, so
        I'm not concerned about performance here (I think it's N for normal
        input, or N^3 worst case).
        """
        part = self.partial_loops[:]
        iterations = 0
        change_made = True
        while change_made:
            iterations += 1
            change_made = False
            for i in range(len(part) - 1, -1, -1):
                # Join (doesn't need to check for final item), and order doesn't
                # matter here because two halves can be joined in either order
                for j in range(len(part) - 1, i, -1):
                    if part[i][-1] == part[j][0]:
                        part[i].extend(part[j][1:])
                        del part[j]
                        change_made = True

                # Promote if `i` is now closed
                if len(part[i]) >= 3 and part[i][0] == part[i][-1]:
                    part[i].pop(-1)
                    self.full_loops.append(Loop(part.pop(i)))
                    # Doesn't set flag, on purpose?

            if iterations > 10:
                logger.warning(
                    "Closing loops is taking a while, iteration %d", iterations
                )

        logger.warning("Closing loops took %d iterations", iterations)

        if part:
            logger.warning("Ignoring leftover partial loops: %r", part)
        self.partial_loops[:] = part

    def parent_info(self) -> dict[int, set[int]]:
        # depth, immediate parent idx
        inside = {i: set() for i in range(len(self.full_loops))}
        for i in range(len(self.full_loops)):
            pt = self.full_loops[i].points[0]  # arbitrarily
            for j in range(len(self.full_loops)):
                if i != j:
                    if pt in self.full_loops[j]:
                        inside[i].add(j)
        return inside

    def fixup(self) -> None:
        pass

    def bounds(self) -> tuple[int, int, int, int]:
        min_x = min(v.x for loop in self.full_loops for v in loop.points)
        max_x = max(v.x for loop in self.full_loops for v in loop.points)
        min_y = min(v.y for loop in self.full_loops for v in loop.points)
        max_y = max(v.y for loop in self.full_loops for v in loop.points)
        return (min_x, max_x, min_y, max_y)


class Job:
    outer: Loop  # for example, stock boundary for facing
    inner: list[Poly]  # for example, pockets or holes

    def __init__(self, outer, inner) -> None:
        self.outer = outer
        self.inner = inner

    def __repr__(self):
        return "%s(outer=%s, inner=%s)" % (
            self.__class__.__name__,
            self.outer,
            self.inner,
        )
