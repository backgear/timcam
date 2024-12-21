from __future__ import annotations
import keke

from logging import getLogger
from timcam.base_steps import Step
from timcam.types import Loop

from toposort import toposort

from timcam.tc2 import PocketStep, ProfileStep

logger = getLogger(__name__)


class ProcessShapes(Step):
    def __init__(self, jumble, **kwargs) -> None:
        self._jumble = jumble
        super().__init__(**kwargs)

    def run(self):
        # TODO this should obey some sort of config for identification.  Right
        # now, we assume outermost is a profile, next inner is profile [with
        # opposite offset direction] and pocket boundary, and next are islands.
        # And even-odd repeat past there, pocket/island

        parents = self._jumble.parent_info()

        self.jobs = jobs = []
        islands: dict[int, tuple[set[int], Loop]] = {}

        n = 0
        for depth, loop_indices in reversed(list(enumerate(toposort(parents)))):
            logger.debug("depth=%s indices=%s", depth, loop_indices)
            if depth == 0:
                for i in loop_indices:
                    jobs.append(
                        ProfileStep(
                            self._jumble.full_loops[i],
                            key=self._key + (n,),
                            status=self._status,
                        )
                    )
                    n += 1
            elif depth % 2:
                # inside [=outside of a pocket]
                inner_islands = []
                for k, v in list(islands.items()):
                    if loop_indices & v[0]:
                        inner_islands.append(v[1])
                        islands.pop(k)

                for i in loop_indices:
                    jobs.append(
                        PocketStep(
                            self._jumble.full_loops[i],
                            islands=inner_islands,
                            key=self._key + (n,),
                            status=self._status,
                        )
                    )
                    n += 1
                    jobs.append(
                        ProfileStep(
                            self._jumble.full_loops[i],
                            key=self._key + (n,),
                            status=self._status,
                        )
                    )
                    n += 1
                    for island in inner_islands:
                        jobs.append(
                            ProfileStep(
                                island, key=self._key + (n,), status=self._status
                            )
                        )
                        n += 1
            else:
                # outside [=island of a pocket]
                for i in loop_indices:
                    islands[i] = (parents[i], self._jumble.full_loops[i])

        assert not islands

        logger.debug("%d jobs:", len(jobs))
        for j in jobs:
            logger.debug("  %r", j)
            self._status.executor.submit(j.lifecycle)

    def preview(self, ctx):
        # ctx.set_fill_rule(cairo.FILL_RULE_WINDING)

        for j in self.jobs:
            if isinstance(j, ProfileStep):
                loop = j._outline
                ctx.move_to(*loop.points[-1])
                for v in loop.points:
                    ctx.line_to(*v)
                with keke.kev("render", cls=j.__class__.__name__):
                    ctx.set_source_rgb(0.5, 0.5, 0.5)
                    ctx.set_line_width(50)
                    ctx.stroke()
            elif isinstance(j, PocketStep):
                for loop in (j._outline, *j._islands):
                    ctx.move_to(*loop.points[-1])
                    for v in loop.points:
                        ctx.line_to(*v)

                with keke.kev("render", cls=j.__class__.__name__):
                    ctx.set_source_rgb(0.7, 0.7, 0.7)
                    ctx.set_line_width(50)
                    ctx.fill()
                    ctx.stroke()
            else:
                raise NotImplementedError(j)
