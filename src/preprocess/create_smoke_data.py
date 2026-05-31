"""파이프라인 smoke test용 더미 프레임 생성."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from src.preprocess.build_metadata import build_metadata
from src.utils.config import load_config, project_root


def _write_frames(out_dir: Path, n_frames: int, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    for i in range(n_frames):
        arr = rng.integers(0, 256, (224, 224, 3), dtype=np.uint8)
        Image.fromarray(arr).save(out_dir / f"frame_{i:06d}.jpg")


def create_smoke_data(frames_root: Path, metadata_csv: Path, cfg: dict) -> None:
    spec = {
        "park_normal": [("vid_a", 5), ("vid_b", 5), ("vid_c", 5), ("vid_d", 5)],
        "anomaly": [("vid_x", 5), ("vid_y", 5)],
        "ucf101": [("Typing__v1", 3)],
    }
    for dataset, videos in spec.items():
        for vid, n in videos:
            _write_frames(frames_root / dataset / vid, n, seed=hash(vid) % 10000)

    build_metadata(frames_root, metadata_csv, cfg)
    print(f"Smoke data ready: {metadata_csv}")


def main() -> None:
    root = project_root()
    cfg = load_config(root / "configs/default.yaml", root / "configs/local.yaml")
    parser = argparse.ArgumentParser(description="Create dummy frames for pipeline test")
    parser.add_argument("--frames-dir", type=Path, default=Path(cfg["paths"]["frames_dir"]))
    parser.add_argument("--metadata", type=Path, default=Path(cfg["paths"]["metadata_csv"]))
    args = parser.parse_args()
    create_smoke_data(args.frames_dir, args.metadata, cfg)


if __name__ == "__main__":
    main()
