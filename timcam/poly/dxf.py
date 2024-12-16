import ezdxf

from .base import Polygon, PolygonJumble

def load_file(fn):
    j = PolygonJumble()
    e = ezdxf.readfile(fn)
    for line in e.modelspace().query("LINE"):
        j.add_line(vec_as_2tuple(line.dxf.start), vec_as_2tuple(line.dxf.end))
    # TODO polyline
    p = j.as_polygon()
    return p

def vec_as_2tuple(v):
    return (v.x, v.y)

if __name__ == "__main__":
    import sys
    from vmodule import vmodule_init
    vmodule_init(10, "ezdxf=-1")
    p = load_file(sys.argv[1])
    p.show(voronoi=True)
