"""data/raw 하위 디렉터리 생성."""

from __future__ import annotations

from pathlib import Path

from src.utils.config import project_root

DATASETS = ("ucf101", "kth", "park_normal", "pedestrian_cctv", "anomaly", "downloads")


def setup_dirs(base: Path | None = None) -> None:
    root = base or project_root() / "data" / "raw"
    for name in DATASETS:
        (root / name).mkdir(parents=True, exist_ok=True)
    (project_root() / "data" / "processed" / "frames").mkdir(parents=True, exist_ok=True)
    print(f"Created directories under {root}")


if __name__ == "__main__":
    setup_dirs()
