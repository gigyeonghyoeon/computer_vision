"""PyTorch Dataset — metadata.csv 기반."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset

from src.utils.transforms import get_transform


class FrameDataset(Dataset):
    def __init__(
        self,
        metadata_csv: str | Path,
        split: str | None = None,
        label: int | None = None,
        train_normal_only: bool = False,
        image_size: int = 224,
        train: bool = False,
    ):
        df = pd.read_csv(metadata_csv)
        if split is not None:
            df = df[df["split"] == split]
        if label is not None:
            df = df[df["label"] == label]
        if train_normal_only:
            df = df[df["label"] == 0]
        self.df = df.reset_index(drop=True)
        self.transform = get_transform(image_size, train=train)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict:
        row = self.df.iloc[idx]
        img = Image.open(row["frame_path"]).convert("RGB")
        tensor = self.transform(img)
        return {
            "image": tensor,
            "label": torch.tensor(row["label"], dtype=torch.long),
            "video_id": row["video_id"],
            "frame_path": row["frame_path"],
        }
