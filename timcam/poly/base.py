from __future__ import annotations

import math
from dataclasses import dataclass
from logging import getLogger

import cairo
from PIL import Image
from pyvoronoi import Pyvoronoi
logger = getLogger(__name__)

def _lines(it):
    t = list(it)
    for i, j in zip(t, t[1:] + t[:1]):
        yield i, j

def to_pil(surface: cairo.ImageSurface) -> Image:
    format = surface.get_format()
    size = (surface.get_width(), surface.get_height())
    stride = surface.get_stride()

    with surface.get_data() as memory:
        if format == cairo.Format.RGB24:
            return Image.frombuffer(
                "RGB", size, memory.tobytes(),
                'raw', "BGRX", stride)
        elif format == cairo.Format.ARGB32:
            return Image.frombuffer(
                "RGBA", size, memory.tobytes(),
                'raw', "BGRa", stride)
        else:
            raise NotImplementedError(repr(format))

# TODO make this way more dynamic
SHOW_SCALE_FACTOR = 50 # px per mm?

@dataclass
class Polygon:
    """
    """
    vertices: list[tuple[int, int]]
    holes: list[list[tuple[int, int]]]

    def __repr__(self):
        return "Polygon(vertices=list[%s], holes=%s)" % (
            len(self.vertices), [f"list[{len(x)}]" for x in self.holes]
        )

    def bounds(self):
        x1 = min(v[0] for v in self.vertices)
        x2 = max(v[0] for v in self.vertices)
        y1 = min(v[1] for v in self.vertices)
        y2 = max(v[1] for v in self.vertices)
        return (x1, x2, y1, y2)

    def show(self, voronoi):
        bounds = self.bounds()
        w = bounds[1] - bounds[0]
        h = bounds[3] - bounds[2]
        wpx = max(int(w * SHOW_SCALE_FACTOR), 1)
        hpx = max(int(h * SHOW_SCALE_FACTOR), 1)

        print(wpx, hpx)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, wpx, hpx)
        ctx = cairo.Context(surf)
        ctx.translate(-bounds[0]*SHOW_SCALE_FACTOR, -bounds[2]*SHOW_SCALE_FACTOR)
        ctx.scale(SHOW_SCALE_FACTOR, SHOW_SCALE_FACTOR)

        ctx.move_to(*self.vertices[0])
        for v in self.vertices[1:]:
            ctx.line_to(*v)
        ctx.close_path()

        for hole in self.holes:
            ctx.move_to(*hole[0])
            for v in hole[1:]:
                ctx.line_to(*v)
            ctx.close_path()

        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.1)
        ctx.stroke()

        if voronoi:
            v = self.voronoi()
            vertices = v.GetVertices()
            edges = v.GetEdges()
            segments = v.GetSegments()
            
            # These are scaled integers, and should dedup nicely
            input_points = set()
            for x in v.inputSegments:
                input_points.add(tuple(x[0]))
                input_points.add(tuple(x[1]))
            original = [
                (
                    int(round(i.X * v.SCALING_FACTOR)),
                    int(round(i.Y * v.SCALING_FACTOR))
                )
                in input_points for i in vertices
            ]

            def mark_pt(pt, rad=0.2):
                ctx.arc(pt.X, pt.Y, rad, -2*math.pi, 0)
                ctx.stroke()

            def mark_line(pt1, pt2):
                ctx.move_to(pt1.X, pt1.Y)
                ctx.line_to(pt2.X, pt2.Y)
                ctx.stroke()
                

            for e_id, e in enumerate(edges):
                if e.is_primary and e.start != -1 and e.end != -1:
                    cell = v.GetCell(e.cell)
                    # TODO docs say e.site1 is a thing, but it doesn't appear to exist

                    #elif cell.contains_segment:
                    #    # TODO should be line-to-point distance

                    #    #ctx.set_source_rgb(1, 1, 0)
                    #    #other = vertices[edges[cell.site].start]
                    #    #mark_pt(other)


                    print(e.start, e.end, len(original), len(vertices))
                    if original[e.start] or original[e.end]:
                        ctx.set_source_rgb(0.3, 0.3, 0.3)  # gray
                        mark_line(vertices[e.start], vertices[e.end])
                    elif e.is_linear:
                        if cell.contains_point:
                            ctx.set_source_rgb(1, 0, 0)
                            pt1 = vertices[e.start]
                            pt2 = vertices[e.end]
                            other = vertices[cell.site]
                            mark_pt(pt1, distance([pt1.X, pt1.Y], [other.X, other.Y]))
                            mark_pt(pt2, distance([pt2.X, pt2.Y], [other.X, other.Y]))
                        elif cell.contains_segment:
                            ctx.set_source_rgb(1, 0, 1)
                            pt1 = vertices[e.start]
                            pt2 = vertices[e.end]
                            # cell.site indexes into segments, not edges (and we don't have scaled segments handy)
                            other1 = [
                                segments[cell.site][0][0] / v.SCALING_FACTOR,
                                segments[cell.site][0][1] / v.SCALING_FACTOR
                            ]
                            other2 = [
                                segments[cell.site][1][0] / v.SCALING_FACTOR,
                                segments[cell.site][1][1] / v.SCALING_FACTOR
                            ]
                                
                            d1 = pt_line_distance(
                                [pt1.X, pt1.Y],
                                other1,
                                other2
                            )
                            print("D", e.start, e.end, d1, [pt1.X, pt1.Y], other1, other2)
                            # d2 = pt_line_distance(
                            #     [pt2.X, pt2.Y],
                            #     [other1.X, other1.Y],
                            #     [other2.X, other2.Y],
                            # )
                            mark_pt(pt1, d1)
                            # mark_pt(pt2, d2)
                        ctx.set_source_rgb(0.2, 0.2, 1) # blue
                        mark_line(vertices[e.start], vertices[e.end])
                    else:
                        v1 = vertices[e.start]
                        v2 = vertices[e.end]
                        max_distance  = distance([v1.X, v1.Y], [v2.X, v2.Y]) / 10
                        moved = False
                        ctx.set_source_rgb(0.2, 1, 0.1) # bright green
                        for pt in v.DiscretizeCurvedEdge(e_id, max_distance):
                            if moved:
                                ctx.line_to(*pt)
                            else:
                                ctx.move_to(*pt)
                                moved = True
                        ctx.stroke()
                        

        surf.write_to_png("example.png")
        im = to_pil(surf)
        im.show()
        
    def voronoi(self):
        v = Pyvoronoi(1024)
        for line in _lines(self.vertices):
            v.AddSegment(line)
        for hole in self.holes:
            for line in _lines(hole):
                v.AddSegment(line)
        v.Construct()
        return v
            


class PolygonJumble:
    def __init__(self):
        self.partial_loops = []

    def add_line(self, pt1, pt2):
        for i, p in enumerate(self.partial_loops):
            if p[-1] == pt1:
                p.append(pt2)
                break
        else:
            logger.debug("New loop %s", pt1)
            self.partial_loops.insert(0, [pt1, pt2])

    def as_polygon(self) -> Polygon:
        closed_loops = []
        # TODO combine partials that were just "backwards" until it stabilizes?
        for partial in self.partial_loops:
            if len(partial) >= 3 and partial[0] == partial[-1]:
                partial.pop(-1)
                closed_loops.append(partial)
            else:
                logger.warning("Ignoring leftover partial loop: %r", partial)
        # TODO correctly decide what is the enclosing one
        # TODO consider more than one level of holes
        return Polygon(closed_loops[-1], closed_loops[:-1])
            
        
def distance(u, v):
    dx = v[0] - u[0]
    dy = v[1] - u[1]
    return ((dx * dx) + (dy * dy)) ** 0.5

def pt_line_distance(p, a, b):
    x0, y0 = p
    x1, y1 = a
    x2, y2 = b
    return abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / ((y2 - y1)**2 + (x2 - x1) ** 2) ** 0.5
