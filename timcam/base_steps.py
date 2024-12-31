from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from logging import getLogger
from typing import Optional
import keke
import cairo
import threading

# from .cairo_pil import to_pil

logger = getLogger(__name__)


class Step:
    def __init__(self, key: tuple[int, ...], status: Status) -> None:
        self._key = key
        self._status = status

    def preview(self, ctx: cairo.Context) -> None:
        raise NotImplementedError

    # TODO better error reporting back to status object too, this ~always
    # happens in threads.
    @keke.ktrace()
    def lifecycle(self):
        self._status.report(self._key, done=False, error=False, obj=self)
        try:
            with keke.kev(self.__class__.__name__, key=str(self._key)):
                self.run()
        except Exception:
            logger.exception("lifecycle")
            self._status.report(self._key, done=True, error=True, obj=self)
        else:
            self._status.report(self._key, done=True, error=False, obj=self)

    def run(self):
        raise NotImplementedError


class LoadStep(Step):
    def __init__(self, path: Path, **kwargs) -> None:
        self._path = path
        super().__init__(**kwargs)


class Status:
    viewport_size = (1920, 1080)
    cairo_matrix: Optional[cairo.Matrix] = None

    def __init__(self, threads, save_previews=False) -> None:
        self.executor = ThreadPoolExecutor(max_workers=threads)
        self.next_file_number = 0
        self.results = {}
        self._pending = 0
        self._done = False
        self._condition = threading.Condition()
        self.save_previews = save_previews

    @keke.ktrace()
    def report(self, key: tuple[int, ...], done: bool, error: bool, obj: Step) -> None:
        logger.info("reporting %s done=%s", key, done)
        if error:
            with self._condition:
                self._done = True
                self._condition.notify_all()
        if done:
            self.results[key] = obj
            if self.save_previews:
                try:
                    img = self.get_preview(obj)
                    with keke.kev("write_to_png"):
                        img.write_to_png(
                            "preview/%s.png" % (".".join(str(i) for i in key))
                        )
                        # im = to_pil(img)
                        # im.save("preview/%s.png" % (".".join(str(i) for i in key)))
                except Exception:
                    logger.exception(".".join(str(i) for i in key))
            self._pending -= 1
            with self._condition:
                if self._pending == 0:
                    self._done = True
                    self._condition.notify_all()

    def get_preview(self, obj: Step) -> cairo.ImageSurface:
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.viewport_size)
        ctx = cairo.Context(img)
        ctx.set_matrix(self.cairo_matrix)
        with keke.kev(
            "preview",
            cls=obj.__class__.__name__,
        ):
            obj.preview(ctx)
        return img

    def set_bounds(self, bounds: tuple[int, int, int, int]) -> None:
        w = bounds[1] - bounds[0]
        h = bounds[3] - bounds[2]
        x = bounds[0]
        y = bounds[3]
        mx = (bounds[0] + bounds[1]) / 2
        my = (bounds[2] + bounds[3]) / 2
        self.cairo_matrix = cairo.Matrix()
        sx = self.viewport_size[0] / w
        sy = self.viewport_size[1] / h
        self.cairo_matrix.translate(
            self.viewport_size[0] / 2, self.viewport_size[1] / 2
        )
        self.cairo_matrix.scale(min(sx, sy), -min(sx, sy))
        self.cairo_matrix.translate(-mx, -my)

    def submit(self, func):
        self._pending += 1
        return self.executor.submit(func)

    def wait(self) -> None:
        i = 1
        while not self._done:
            with self._condition:
                if not self._done:
                    result = self._condition.wait(1)

            logger.warning("After %d seconds, %d pending", i, self._pending)
            i += 1
        self.executor.__exit__(None, None, None)
