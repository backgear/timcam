from __future__ import annotations
from math import atan2, pi as PI
from typing import Generator

import cairo
import pyvoronoi

from .point import Point
from .poly import Poly
from .line import Polyline, VariableWidthPolyline
from ..algo import pt_line_distance, angle_similarity

INSIDE = 1
TERMINAL = 2


class Voronoi:
    """
    Voronoi diagram of a Poly -- single outer loop minus optional holes.

    Winding order of the polygon _does not matter_.

    This wraps some complexity of the getters in pyvoronoi, and if this is more
    generally useful should get upstreamed.

    Everything is implementation details except `get_dag()`
    """

    def __init__(self, poly: Poly) -> None:
        self._raw = pyvoronoi.Pyvoronoi(1)
        for line in poly.line_iter():
            self._raw.AddSegment(line)
        self._raw.Construct()

        self.edge_points = set(poly.point_iter())
        self.vertex_indices_on_edge: set[int] = set()
        self.vertex_indices_inside: set[int] = set()

        for i, v in enumerate(self._raw.GetVertices()):
            pt = Point.from_pyvoronoi_vec(v)
            if pt in self.edge_points:
                self.vertex_indices_on_edge.add(i)
            elif pt in poly:
                self.vertex_indices_inside.add(i)

        # This part can be simplified once there's a fix for
        # https://github.com/fabanc/pyvoronoi/issues/42
        self.vertex_outgoing_edges: dict[int, list[int]] = {}
        for i, e in enumerate(self._raw.GetEdges()):
            self.vertex_outgoing_edges.setdefault(e.start, []).append(i)

    def draw(self, ctx: cairo.Context) -> None:
        """
        Render this diagram to a context

        Notes:
        1. Only draws curved edges as if they were straight
        2. Does not draw the original input points [do that yourself first]
        3. Does not color code anything
        """
        vertices = self._raw.GetVertices()
        for i, e in enumerate(self._raw.GetEdges()):
            if e.start != -1 and e.end != -1:
                ctx.move_to(vertices[e.start].X, vertices[e.start].Y)
                ctx.line_to(vertices[e.end].X, vertices[e.end].Y)
        ctx.set_source_rgb(0.5, 0.5, 1)
        ctx.stroke()

    def dag(self, path_threshold=1.0) -> Dag:
        """
        Compute a DAG for this Voronoi diagram, that contains all _useful_ nodes.

        `path_threshold` is the minimum whisker length to leave; real-world
        polygons tend to have about half the paths unhelpful for medial line
        calculation.
        """
        vii = self.vertex_indices_inside
        vioe = self.vertex_indices_on_edge

        edges: dict[int, DagEdge] = {}

        for i, e in enumerate(self._raw.GetEdges()):
            if e.start == -1 or e.end == -1:
                # remove infinite-only edges, because if we forget and pass -1 to
                # GetVertex it will crash :/
                # See https://github.com/fabanc/pyvoronoi/issues/41
                continue

            # This flag is only used for color-coding in Dag today, but having
            # it makes the `if` structure a lot more obvious.
            flag = 0
            if e.start in vii and e.end in vii:
                flag = INSIDE
            elif e.start in vii and e.end in vioe:
                flag = TERMINAL
            else:
                # 1. Excludes edges that _begin_ at any polygon edge; those are
                # uninteresting because the only way to reach them is from other
                # edges we'd rather visit first.
                # 2. Excludes edges that are entirely outside the polygon, those
                # will never be part of the inside skeleton
                continue

            edges[i] = DagEdge(self._raw, i, flag)

        # This constructs a graph with many trivial cycles; these are removed in
        # the Dag constructor.
        for i, edge in edges.items():
            for v in self.vertex_outgoing_edges.get(edge._edge.end, ()):
                if v in edges:
                    edge.next.append(edges[v])

        # Choose the item with the largest inscribed circle, breaking ties
        # towards the right (ties are broken to make testing easier; right
        # chosen for standard endmills cutting conventionally this means more of
        # the chips are thrown behind the machine).
        lic_vertex_idx = max(
            edges.items(),
            key=(lambda x: (x[1].start_rad, x[1].start_pt.x, x[1].start_pt.y)),
        )[1]._edge.start

        # N.b. there are references to the values from our `edges` in what we're
        # setting here; that's how the children get included.
        d = Dag(self._raw, lic_vertex_idx)
        for i in self.vertex_outgoing_edges[lic_vertex_idx]:
            if i in edges:
                d.next.append(edges[i])
                d.start_rad = edges[i].start_rad
        return d.simplify()


class BaseDag:
    next: list[BaseDag]

    def visit_preorder(self, parent=None) -> Generator[BaseDag, None, None]:
        yield (parent, self)
        for x in self.next:
            yield from x.visit_preorder(parent=self)

    def visit_postorder(self, parent=None) -> Generator[BaseDag, None, None]:
        for x in self.next:
            yield from x.visit_postorder(parent=self)
        yield (parent, self)


class Dag(BaseDag):
    def __init__(self, vor: pyvoronoi.Pyvoronoi, starting_vertex: int):
        self.start_pt = Point.from_pyvoronoi_vec(vor.GetVertex(starting_vertex))
        self.start_rad = None
        self._edge_idx = None
        self.next = []

    def length(self):
        return 0.0

    def simplify(self, min_productive_length=1.0):
        """
        After adding items to `self.next`, call this to remove unnecessary paths
        (that are short and unproductive), and ensures that extra edges get
        removed so it is actually a DAG.

        This can probably be done more with fewer visits, but split out to be
        more understandable.
        """
        # 1. Ensure edges all have a parent set
        # 2. Filter out non-optimal paths [by hop count]; this is more about
        # removing the opposing half-edges than optimizing the cut path.
        seen: set[int] = set()
        for parent_edge, this_edge in self.visit_preorder():
            seen.add(this_edge._edge_idx)

            this_edge.parent = parent_edge
            this_edge.next = [
                edge
                for edge in this_edge.next
                if edge._edge_idx not in seen and edge._edge.twin not in seen
            ]

        # Calculate bottom-up length (to the edge of the circle at the tip,
        # typically zero)
        for parent_edge, this_edge in self.visit_postorder():
            if not this_edge.next:
                this_edge.path_length = this_edge.length() + this_edge.end_rad
            else:
                this_edge.path_length = this_edge.length() + max(
                    [e.path_length for e in this_edge.next]
                )

        # Remove unproductive whiskers
        for parent_edge, this_edge in self.visit_preorder():
            this_edge.next = [
                edge
                for edge in this_edge.next
                if edge.path_length - self.start_rad > min_productive_length
            ]
            this_edge.next.sort(key=lambda e: (e.path_length, -e.end_pt.y, e.end_pt.x))
        return self

    def draw(self, ctx):
        for parent_edge, this_edge in self.visit_postorder():
            if parent_edge is None:
                continue
            ctx.move_to(*this_edge.start_pt)
            ctx.line_to(*this_edge.end_pt)
        ctx.set_source_rgb(0, 0, 1)
        ctx.set_line_width(50)
        ctx.stroke()


class DagEdge(BaseDag):
    def __init__(self, vor: pyvoronoi.Pyvoronoi, edge_idx: int, flag: int) -> None:
        self._edge_idx = edge_idx
        self._edge = vor.GetEdge(edge_idx)

        cell = vor.GetCell(self._edge.cell)
        try:
            if cell.contains_point:
                self.site_pt1 = Point(*vor.RetrievePoint(cell))
                self.site_pt2 = None
            else:
                values = vor.RetrieveSegment(cell)
                self.site_pt1 = Point(*values[0])
                self.site_pt2 = Point(*values[1])
        except IndexError:
            print(
                "XXX",
                self._edge.cell,
                cell.cell_identifier,
                cell.vertices,
                cell.source_category,
                cell.site,
                cell.is_open,
                cell.edges,
            )
            print("XXX linear", self._edge.is_linear)
            print("XXX", Point.from_pyvoronoi_vec(vor.GetVertex(self._edge.start)))
            print("XXX", Point.from_pyvoronoi_vec(vor.GetVertex(self._edge.end)))
            print("XXX", cell.contains_point)
            print("XXX", vor.inputSegments)
            raise

        self.start_pt = Point.from_pyvoronoi_vec(vor.GetVertex(self._edge.start))
        self.end_pt = Point.from_pyvoronoi_vec(vor.GetVertex(self._edge.end))
        self.vector = self.end_pt - self.start_pt
        self.start_rad = self._rad(self.start_pt)
        self.end_rad = self._rad(self.end_pt)

        self.next = []

    def _rad(self, pt):
        if self.site_pt2 is None:
            return pyvoronoi.Distance(pt, self.site_pt1)
        else:
            return pt_line_distance(pt, self.site_pt1, self.site_pt2)

    def length(self):
        return self.vector.length()


class DagMultiEdge(BaseDag):
    def __init__(self, other: DagEdge) -> None:
        self._edges = []
        self.prepend(other)

    def prepend(self, other: DagEdge) -> None:
        if (
            angle_similarity(self._edges[-1].vector, other.vector) > 0.5
        ):  # TODO magic number
            raise TooDifferent()
        self._edges.insert(0, other)
        self.start_pt = self._edges[0].start_pt
        self.start_rad = self._edges[0].start_rad
        self.end = self._edges[-1].end_pt
        self.end_rad = self._edges[-1].end_rad

    def draw(self, ctx):
        for e in self._edges:
            e.draw(ctx)
