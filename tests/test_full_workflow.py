from concurrent.futures import Future
from pathlib import Path
from timcam.api import Main
from timcam.tc2 import PocketStep, ProfileStep


class LockstepMain(Main):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending = []

    def submit(self, func):
        self.pending.append(func)
        f = Future()
        f.set_result(None)
        return f

    def unblock(self):
        with self._condition:
            self._done = False
            while self.pending:
                super().submit(self.pending.pop(0))


def test_full_workflow():
    m = LockstepMain(1)
    m.load(Path("tests/shapes/11_5spot.dxf"))
    m.unblock()
    with m._condition:
        m._condition.wait(5)
    assert m._done
    tc0_loader = m.results[(0,)]
    assert len(tc0_loader.jumble.full_loops) == 7
    # 5 spots, which are islands in a pocket (1) and the part has an outside
    # boundary (0). Indices here come from what openscad produced, which is
    # outside-in.
    assert tc0_loader.jumble.parent_info() == {
        6: {0, 1},
        5: {0, 1},
        4: {0, 1},
        3: {0, 1},
        2: {0, 1},
        1: {0},
        0: set(),
    }
    preview = m.get_preview(tc0_loader)
    # TODO validate image

    m.unblock()
    with m._condition:
        m._condition.wait(5)
    assert m._done
    tc1_process_shapes = m.results[(0, 0)]
    preview = m.get_preview(tc1_process_shapes)
    # TODO validate image

    m.unblock()
    with m._condition:
        m._condition.wait(5)
    assert m._done

    assert isinstance(m.results[(0, 0, 0)], PocketStep)
    pocket = m.results[(0, 0, 0)]
    assert len(pocket._islands) == 5
    # 7mm dia + 2mm offset each side as microns
    assert width(pocket._offset_islands[0]) == 11000
    preview = m.get_preview(pocket)
    # TODO validate image

    assert isinstance(m.results[(0, 0, 1)], ProfileStep)
    inside_profile = m.results[(0, 0, 1)]
    assert width(inside_profile._offset_outlines[0]) == 46000

    assert isinstance(m.results[(0, 0, 2)], ProfileStep)
    assert isinstance(m.results[(0, 0, 3)], ProfileStep)
    assert isinstance(m.results[(0, 0, 4)], ProfileStep)
    assert isinstance(m.results[(0, 0, 5)], ProfileStep)
    assert isinstance(m.results[(0, 0, 6)], ProfileStep)
    one_spot = m.results[(0, 0, 6)]
    assert width(one_spot._offset_outlines[0]) == 11000

    assert isinstance(m.results[(0, 0, 7)], ProfileStep)
    outside_profile = m.results[(0, 0, 7)]
    assert width(outside_profile._offset_outlines[0]) == 74000
    preview = m.get_preview(outside_profile)


def width(lst):
    xs = [i[0] for i in lst]
    return max(xs) - min(xs)
