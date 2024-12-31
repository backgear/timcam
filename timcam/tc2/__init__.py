from __future__ import annotations

import logging
import sys

import cairo
import keke
import pyclipper

from timcam.types import Point, Poly, Voronoi, Loop
from timcam.base_steps import Step
from timcam.tc3 import SpiralStep, AsymmetricStadiumStep

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
        # TODO why am I passing around these two things rather than just storing
        # a poly on self?
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

        pc.Clear()
        for isl in self._islands:
            pc.AddPath(isl.points, pyclipper.JT_SQUARE, pyclipper.ET_CLOSEDPOLYGON)

        if self._outline.direction() < 0:
            self._offset_islands = pc.Execute(2000)  # 2mm
        else:
            self._offset_islands = pc.Execute(-2000)  # 2mm

        with keke.kev("pyvoronoi"):
            self.vors = [
                Voronoi(
                    Poly(
                        Loop([Point(*i) for i in x]),
                        [Loop([Point(*i) for i in y]) for y in self._offset_islands],
                    )
                )
                for x in self._offset_outlines
            ]

        with keke.kev("traverse"):
            jobs = []
            n = 0
            self.dags = []
            for vor in self.vors:
                dag = vor.dag()
                self.dags.append(dag)
                jobs.append(
                    SpiralStep(
                        dag.start_pt,
                        dag.start_rad,
                        key=self._key + (n,),
                        status=self._status,
                    )
                )
                n += 1
                # TODO visit to make polyline
                for parent_edge, this_edge in dag.visit_preorder():
                    if parent_edge is None:
                        continue
                    jobs.append(
                        AsymmetricStadiumStep(
                            this_edge.line,
                            key=self._key + (n,),
                            status=self._status,
                        )
                    )
                    n += 1

        for j in jobs:
            self._status.submit(j.lifecycle)

    def preview(self, ctx):
        # cut width
        for pts in self._offset_outlines:
            ctx.move_to(*pts[-1])
            for v in pts:
                ctx.line_to(*v)
            ctx.close_path()
        ctx.set_source_rgb(0.7, 0.7, 0.7)
        ctx.set_line_width(4000)  # 4mm
        ctx.set_line_join(cairo.LineJoin.ROUND)
        ctx.stroke()

        ctx.set_line_width(50)
        for vor in self.vors:
            vor.draw(ctx)
        for dag in self.dags:
            dag.draw(ctx)
