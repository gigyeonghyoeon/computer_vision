"""Split 요약 출력 + normal_classes 검증."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from src.utils.config import project_root


def print_split_summary(metadata_csv: Path) -> None:
    df = pd.read_csv(metadata_csv)
    print("=== Split summary (videos) ===")
    video_df = df.drop_duplicates("video_id")
    summary = (
        video_df.groupby(["split", "dataset", "label"])
        .size()
        .reset_index(name="videos")
    )
    print(summary.to_string(index=False))
    print(f"\nTotal: {video_df['video_id'].nunique()} videos, {len(df)} frames")


def validate_normal_classes(raw_dir: Path, classes_yaml: Path) -> None:
    with open(classes_yaml, encoding="utf-8") as f:
        classes = yaml.safe_load(f)

    for dataset, expected in classes.items():
        ds_dir = raw_dir / dataset
        if not ds_dir.exists():
            print(f"[skip] {dataset}: directory not found")
            continue
        found = sorted({p.parent.name for p in ds_dir.rglob("*.mp4")})
        if not found:
            found = sorted({p.name for p in ds_dir.iterdir() if p.is_dir()})
        missing = set(expected) - set(found)
        extra = set(found) - set(expected)
        print(f"\n=== {dataset} ===")
        print(f"  expected: {len(expected)} classes")
        if missing:
            print(f"  missing:  {sorted(missing)}")
        if extra:
            print(f"  extra:    {sorted(extra)}")
        if not missing and not extra:
            print("  OK — all classes present")


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Validate data split and classes")
    parser.add_argument(
        "--metadata",
        type=Path,
        default=root / "data/processed/metadata.csv",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=root / "data/raw",
    )
    parser.add_argument(
        "--classes",
        type=Path,
        default=root / "configs/normal_classes.yaml",
    )
    args = parser.parse_args()

    if args.metadata.exists():
        print_split_summary(args.metadata)
    else:
        print(f"metadata not found: {args.metadata}")

    validate_normal_classes(args.raw_dir, args.classes)


if __name__ == "__main__":
    main()
