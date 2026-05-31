"""metadata.csv 생성 — frames 디렉터리 스캔 + train/val/test split."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.config import load_config, project_root
from src.utils.seed import set_seed

# dataset 폴더명 → (label, splittable)
DATASET_RULES: dict[str, tuple[int, bool]] = {
    "ucf101": (0, False),
    "kth": (0, False),
    "park_normal": (0, True),
    "pedestrian_cctv": (0, True),
    "anomaly": (1, False),
}


def scan_frames(frames_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for frame_path in sorted(frames_dir.rglob("*.jpg")):
        rel = frame_path.relative_to(frames_dir)
        parts = rel.parts
        if len(parts) < 3:
            continue
        dataset = parts[0]
        video_id = parts[1]
        label, _ = DATASET_RULES.get(dataset, (0, False))
        rows.append(
            {
                "video_id": f"{dataset}__{video_id}",
                "dataset": dataset,
                "label": label,
                "frame_path": str(frame_path),
            }
        )
    return pd.DataFrame(rows)


def assign_splits(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    split_cfg = cfg["split"]
    train_r = split_cfg["train_ratio"]
    val_r = split_cfg["val_ratio"]
    splittable = set(split_cfg["splittable_datasets"])

    df = df.copy()
    df["split"] = "train"

    for dataset in splittable:
        mask = df["dataset"] == dataset
        videos = df.loc[mask, "video_id"].unique()
        if len(videos) == 0:
            continue

        train_v, temp_v = train_test_split(
            videos, test_size=(1 - train_r), random_state=cfg["project"]["seed"]
        )
        val_ratio_of_temp = val_r / (val_r + split_cfg["test_ratio"])
        val_v, test_v = train_test_split(
            temp_v, test_size=(1 - val_ratio_of_temp), random_state=cfg["project"]["seed"]
        )

        df.loc[df["video_id"].isin(train_v), "split"] = "train"
        df.loc[df["video_id"].isin(val_v), "split"] = "val"
        df.loc[df["video_id"].isin(test_v), "split"] = "test"

    # anomaly → test only
    df.loc[df["dataset"] == "anomaly", "split"] = "test"
    return df


def build_metadata(frames_dir: Path, output_csv: Path, cfg: dict) -> pd.DataFrame:
    df = scan_frames(frames_dir)
    if df.empty:
        raise FileNotFoundError(f"No frames found under {frames_dir}")
    df = assign_splits(df, cfg)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"metadata: {len(df)} frames, {df['video_id'].nunique()} videos")
    print(df.groupby(["split", "label"]).size().to_string())
    return df


def main() -> None:
    root = project_root()
    cfg = load_config(root / "configs/default.yaml")
    set_seed(cfg["project"]["seed"])

    parser = argparse.ArgumentParser(description="Build metadata.csv from extracted frames")
    parser.add_argument("--frames-dir", type=Path, default=Path(cfg["paths"]["frames_dir"]))
    parser.add_argument("--output", type=Path, default=Path(cfg["paths"]["metadata_csv"]))
    args = parser.parse_args()

    build_metadata(args.frames_dir, args.output, cfg)


if __name__ == "__main__":
    main()
