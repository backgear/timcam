from __future__ import annotations

import logging
from math import cos, sin, atan2, pi as PI

import cairo
from keke import ktrace

from timcam.types import Point, VariableWidthPolyline
from timcam.base_steps import Step
from timcam.algo import outer_tangents

logger = logging.getLogger(__name__)


class SpiralStep(Step):
    def __init__(self, pt, r, **kwargs):
        self.pt = pt
        self.r = r
        self.initial_r = 500
        self.stepover = 500
        super().__init__(**kwargs)

    @ktrace()
    def run(self):
        rotations = (self.r - self.initial_r) / self.stepover
        # TODO initial helix down
        self.pts = [self.pt]
        # frange?
        for f in range(int(rotations * 100)):
            angle = f / 100 * 2 * PI
            r = self.initial_r + (f / 100) * self.stepover
            x = cos(angle) * r
            y = sin(angle) * r
            self.pts.append(self.pt + Point(x, y))

    def preview(self, ctx):
        ctx.new_sub_path()
        ctx.set_line_width(4000)
        ctx.set_source_rgb(0.9, 0.9, 0.9)
        ctx.move_to(*self.pts[0])
        for pt in self.pts[1:]:
            ctx.line_to(*pt)
        ctx.stroke()

        ctx.new_sub_path()
        ctx.set_line_width(50)
        ctx.set_source_rgb(0, 1, 0)
        # ctx.arc(*self.pt, self.r, 0, PI * 2)
        # ctx.fill()
        ctx.move_to(*self.pts[0])
        for pt in self.pts[1:]:
            ctx.line_to(*pt)
        ctx.stroke()


class AsymmetricStadiumStep(Step):
    def __init__(self, line, **kwargs):
        self.line = line
        self.discretized = None
        super().__init__(**kwargs)

    def run(self) -> None:
        assert self.discretized is None
        self.discretized = list(self.line.iter_width_along(200))  # TODO: magic number

    def approximate_length(self):
        # TODO move this up into traverse?
        center_distance = (self.discretized[-1][0] - self.discretized[0][0]).length()
        return center_distance + self.discretized[-1][1] - self.discretized[0][1]

    def preview(self, ctx: cairo.Context) -> None:
        ctx.set_line_width(50)
        ctx.set_source_rgb(0, 1, 0)
        for pt, r in self.discretized[1:]:
            ctx.new_sub_path()
            ctx.arc(*pt, r + 2000, 0, 2 * PI)
        ctx.stroke()
        # gray, previously-finished cut
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.new_sub_path()
        ctx.arc(*self.discretized[0][0], self.discretized[0][1] + 2000, 0, 2 * PI)
        ctx.fill()

        # ctx.set_source_rgb(0, 1, 0)
        # line1, line2 = outer_tangents(self.pt1, self.r1, self.pt2, self.r2)

        # delta1 = line1[0] - self.pt1
        # delta2 = line2[0] - self.pt1
        # ang1 = atan2(delta1.y, delta1.x)
        # ang2 = atan2(delta2.y, delta2.x)
        # print("ARC", self.pt1, self.r1, ang1, ang2)
        # # if ang2 < ang1:
        # #    ang2 += 2*PI
        # # ctx.arc(
        # #    *self.pt1, self.r1,
        # #    ang2, ang1,
        # # )
        # ctx.new_sub_path()
        # ctx.move_to(*line2[0])
        # ctx.arc(*self.pt1, self.r1, ang2, ang1)
        # ctx.line_to(*line1[1])
        # ctx.arc_negative(*self.pt2, self.r2, ang1, ang2)
        # ctx.close_path()
        # ctx.fill()

        # # green dot
        # ctx.new_sub_path()
        # ctx.set_source_rgb(0, 0.5, 0)
        # ctx.arc(*line2[0], 100, 0, 2 * PI)
        # ctx.fill()
        # # red dot
        # ctx.new_sub_path()
        # ctx.set_source_rgb(1, 0, 0)
        # ctx.arc(*line2[1], 100, 0, 2 * PI)
        # ctx.fill()
