"""AI Hub 다운로드 폴더 → data/raw/{dataset} 정리."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from src.utils.config import project_root

VIDEO_EXT = {".mp4", ".avi", ".mkv", ".MP4", ".AVI"}

# park_normal: 정상행위만 복사
NORMAL_KEYWORDS = ("정상", "normal", "Normal", "NORMAL")
SKIP_KEYWORDS = ("불법", "illegal", "Illegal", "ILLEGAL", "비정상", "anomaly")

# pedestrian / anomaly: 필터 없이 전체 (anomaly는 source가 이미 이상만)
NO_FILTER_DATASETS = {"pedestrian_cctv", "anomaly"}


def _should_include(path: Path, dataset: str) -> bool:
    if dataset in NO_FILTER_DATASETS:
        return True
    text = str(path).lower()
    if any(k.lower() in text for k in SKIP_KEYWORDS):
        return False
    if any(k.lower() in text for k in NORMAL_KEYWORDS):
        return True
    # 경로에 키워드 없으면 park_normal은 제외 (안전)
    return dataset != "park_normal"


def organize(source: Path, dest: Path, dataset: str, copy: bool = True) -> int:
    if not source.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    op = shutil.copy2 if copy else shutil.move

    for video in source.rglob("*"):
        if video.suffix not in VIDEO_EXT:
            continue
        if not _should_include(video, dataset):
            continue
        rel = video.relative_to(source)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists():
            op(video, out)
            count += 1

    print(f"[{dataset}] {count} videos → {dest}")
    return count


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Organize AI Hub downloads into data/raw")
    parser.add_argument("--source", type=Path, required=True, help="Download/extract folder")
    parser.add_argument(
        "--dataset",
        choices=["park_normal", "pedestrian_cctv", "anomaly"],
        required=True,
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Default: data/raw/{dataset}",
    )
    parser.add_argument("--move", action="store_true", help="Copy instead of move (default: copy)")
    args = parser.parse_args()

    dest = args.dest or root / "data" / "raw" / args.dataset
    organize(args.source, dest, args.dataset, copy=not args.move)


if __name__ == "__main__":
    main()
