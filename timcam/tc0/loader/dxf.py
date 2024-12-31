from logging import getLogger

import ezdxf
import keke

from timcam.types import Jumble, Point
from timcam.base_steps import LoadStep
from timcam.tc1 import ProcessShapes

logger = getLogger(__name__)

SCALE_FACTOR = 1_000  # mm -> micron


class LoadDxf(LoadStep):
    def run(self):
        from timcam.algo import lines

        with keke.kev("ezdxf.readfile", filename=str(self._path)):
            e = ezdxf.readfile(self._path)

        self.jumble = j = Jumble()
        # TODO make sure modelspace is correct
        for line in e.modelspace().query("LINE"):
            j.add_line(
                Point.from_dxf_vec(line.dxf.start, SCALE_FACTOR),
                Point.from_dxf_vec(line.dxf.end, SCALE_FACTOR),
            )

        for poly in e.modelspace().query("LWPOLYLINE"):
            points = poly.get_points()
            for pt1, pt2 in zip(points, points[1:]):
                # TODO bendy lines
                j.add_line(
                    Point(float(pt1[0]) * SCALE_FACTOR, float(pt1[1]) * SCALE_FACTOR),
                    Point(float(pt2[0]) * SCALE_FACTOR, float(pt2[1]) * SCALE_FACTOR),
                )

        for arc in e.modelspace().query("ARC"):
            # TODO discretize
            start_point = arc.start_point
            end_point = arc.end_point
            j.add_line(
                Point(start_point[0], start_point[1]),
                Point(end_point[0], end_point[1]),
            )

        with keke.kev("Jumble.close_loops"):
            j.close_loops()
        # N.b. today j only contains "loops" which are easy to get bounds; if
        # fixup transforms to arcs/circles those will be a little more complex
        # to handle.
        self._status.set_bounds(j.bounds())
        with keke.kev("Jumble.fixup"):
            j.fixup()
        self._next = ProcessShapes(j, key=self._key + (0,), status=self._status)
        self._status.submit(self._next.lifecycle)

    def preview(self, ctx) -> None:
        # print(ctx.get_matrix())
        for loop in self.jumble.full_loops:
            ctx.move_to(*loop.points[-1])
            for p in loop.points:
                # print(p, ctx.get_matrix().transform_point(*p))
                ctx.line_to(*p)
            ctx.close_path()

        ctx.set_source_rgb(0.2, 0.2, 0.5)
        ctx.set_line_width(50)
        ctx.stroke()
