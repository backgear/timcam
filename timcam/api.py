from __future__ import annotations
import os
import sys
import logging
import keke
from vmodule import vmodule_init
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .base_steps import Status

from .tc0.loader import load_file_cls


class Main(Status):
    def __init__(self, threads) -> None:
        self.executor = ThreadPoolExecutor(max_workers=threads)
        self.next_file_number = 0
        self._pending = 0

    # TODO the intent is that we might have a config that tells us to load
    # multiple files, like stock, pockets, outlines, and their respective
    # "operations" along with polygons.  This could be called multiple times,
    # incrementing the key.
    def load(self, path: Path) -> None:
        key = (self.next_file_number,)
        self.next_file_number += 1
        obj = load_file_cls(path)(path=path, key=key, status=self)
        n = self.executor.submit(obj.lifecycle)
        n.result()

    def join(self) -> None:
        self.executor.__exit__(None, None, None)


if __name__ == "__main__":
    vmodule_init(logging.DEBUG, "ezdxf=-1")
    # We don't clear out the preview/ dir to make it easier for eog to refresh
    # open files.
    os.makedirs("preview", exist_ok=True)
    with keke.TraceOutput(file=open("trace.out", "w")):
        m = Main(4)
        m.load(Path(sys.argv[1]))
        m.join()
