from __future__ import annotations

import logging

import cairo
import keke
import pyclipper
import pyvoronoi

from timcam.types import Point
from timcam.base_steps import Step
from timcam.types.poly import _lines

logger = logging.getLogger(__name__)


class ProfileStep(Step):
    def __init__(self, outline, **kwargs):
        self._outline = outline
        super().__init__(**kwargs)

    def run(self):
        pc = pyclipper.PyclipperOffset()
        # TODO JT_ROUND and resulting arcs
        pc.AddPath(
            self._outline.points, pyclipper.JT_SQUARE, pyclipper.ET_CLOSEDPOLYGON
        )
        # Pyclipper considers offset to be irrespective of polygon winding
        # order, so we negate when necessary here to offset "outside" or
        # "inside"
        with keke.kev("pyclipper"):
            if self._outline.direction() < 0:
                self._offset_outlines = pc.Execute(-2000)  # 2mm
            else:
                self._offset_outlines = pc.Execute(2000)  # 2mm

    def preview(self, ctx):
        # border
        pts = self._outline.points
        ctx.move_to(*pts[-1])
        for v in pts:
            ctx.line_to(*v)
        ctx.close_path()
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.set_line_width(50)
        ctx.stroke()

        # cut width
        for pts in self._offset_outlines:
            ctx.move_to(*pts[-1])
            for v in pts:
                ctx.line_to(*v)
            ctx.close_path()
        ctx.set_source_rgb(0, 0, 0.5)
        ctx.set_line_width(4000)  # 4mm
        ctx.set_line_join(cairo.LineJoin.ROUND)
        ctx.stroke()
        # cut center
        for pts in self._offset_outlines:
            ctx.move_to(*pts[-1])
            for v in pts:
                ctx.line_to(*v)
            ctx.close_path()
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(50)
        ctx.stroke()


class PocketStep(Step):
    def __init__(self, outline, islands, **kwargs):
        self._outline = outline
        self._islands = islands
        super().__init__(**kwargs)

    def run(self):
        vor = pyvoronoi.Pyvoronoi(1)
        for loop in (self._outline, *self._islands):
            for line in _lines(loop.points):
                vor.AddSegment(line)
        with keke.kev("pyvoronoi"):
            vor.Construct()
            self.vor_edges = vor.GetEdges()
            self.vor_verts = [Point(int(v.X), int(v.Y)) for v in vor.GetVertices()]

    def preview(self, ctx):
        orig = set(self._outline.points)
        for island in self._islands:
            orig.update(island.points)
        good_vert_incides = set()
        for i, v in enumerate(self.vor_verts):
            if v in orig:
                good_vert_incides.add(i)
            elif v in self._outline:
                if not any(v in island for island in self._islands):
                    good_vert_incides.add(i)

        for edge in self.vor_edges:
            if edge.start not in good_vert_incides:
                continue
            if edge.end not in good_vert_incides:
                continue

            ctx.move_to(*self.vor_verts[edge.start])
            ctx.line_to(*self.vor_verts[edge.end])

        with keke.kev("render"):
            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(50)
            ctx.stroke()
