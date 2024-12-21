from pathlib import Path

from timcam.base_steps import LoadStep

from .dxf import LoadDxf


def load_file_cls(p: Path) -> LoadStep:
    if p.suffix == ".dxf":
        return LoadDxf
    else:
        raise NotImplementedError(p)
