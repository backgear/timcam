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
        with keke.kev("ezdxf.readfile", filename=str(self._path)):
            e = ezdxf.readfile(self._path)

        self.jumble = j = Jumble()
        # TODO make sure modelspace is correct
        for line in e.modelspace().query("LINE"):
            j.add_line(
                Point.from_dxf_vec(line.dxf.start, SCALE_FACTOR),
                Point.from_dxf_vec(line.dxf.end, SCALE_FACTOR),
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
        self._status.executor.submit(self._next.lifecycle)

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
