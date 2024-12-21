from __future__ import annotations
from pathlib import Path
from logging import getLogger
from typing import Optional
import keke
import cairo

logger = getLogger(__name__)


class Step:
    def __init__(self, key: tuple[int, ...], status: Status) -> None:
        self._key = key
        self._status = status

    def preview(self, ctx: cairo.Context) -> None:
        raise NotImplementedError

    # TODO better error reporting back to status object too, this ~always
    # happens in threads.
    def lifecycle(self):
        self._status.report(self._key, done=False, obj=self)
        try:
            with keke.kev(self.__class__.__name__, key=str(self._key)):
                self.run()
        except Exception:
            logger.exception("lifecycle")
        self._status.report(self._key, done=True, obj=self)

    def run(self):
        raise NotImplementedError


class LoadStep(Step):
    def __init__(self, path: Path, **kwargs) -> None:
        self._path = path
        super().__init__(**kwargs)


class Status:
    viewport_size = (1920, 1080)
    cairo_matrix: Optional[cairo.Matrix] = None

    def report(self, key: tuple[int, ...], done: bool, obj: Step) -> None:
        logger.info("reporting %s done=%s", key, done)
        if done:
            try:
                img = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.viewport_size)
                ctx = cairo.Context(img)
                ctx.set_matrix(self.cairo_matrix)
                with keke.kev(
                    "preview",
                    key=".".join(str(i) for i in key),
                    cls=obj.__class__.__name__,
                ):
                    obj.preview(ctx)
                img.write_to_png("preview/%s.png" % (".".join(str(i) for i in key)))
            except Exception:
                logger.exception(".".join(str(i) for i in key))

    def set_bounds(self, bounds: tuple[int, int, int, int]) -> None:
        w = bounds[1] - bounds[0]
        h = bounds[3] - bounds[2]
        x = bounds[0]
        y = bounds[3]
        self.cairo_matrix = cairo.Matrix()
        self.cairo_matrix.scale(self.viewport_size[0] / w, self.viewport_size[1] / -h)
        self.cairo_matrix.translate(-x, -y)
