"""PatchCore Memory Bank 구축."""

from __future__ import annotations

import argparse
from pathlib import Path

from torch.utils.data import DataLoader

from src.models.patchcore import PatchCore
from src.preprocess.dataset import FrameDataset
from src.utils.config import get_device, load_config, project_root
from src.utils.seed import set_seed


def build(cfg: dict, backbone: str | None = None) -> Path:
    set_seed(cfg["project"]["seed"])
    device = get_device(cfg)
    pc_cfg = cfg["patchcore"]
    backbone = backbone or pc_cfg["backbone"]
    paths = cfg["paths"]

    dataset = FrameDataset(
        paths["metadata_csv"],
        split="train",
        train_normal_only=True,
        image_size=cfg["preprocess"]["image_size"],
    )
    loader = DataLoader(
        dataset,
        batch_size=pc_cfg["batch_size"],
        shuffle=False,
        num_workers=0,
    )

    model = PatchCore(
        backbone=backbone,
        coreset_ratio=pc_cfg["coreset_ratio"],
        k_neighbors=pc_cfg["k_neighbors"],
        device=device,
    )
    model.fit(loader)

    out_dir = Path(paths["output_dir"]) / "patchcore"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{backbone}_memory.pkl"
    model.save(out_path)
    print(f"Saved memory bank to {out_path}")
    return out_path


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Build PatchCore memory bank")
    parser.add_argument(
        "--config",
        nargs="+",
        default=[str(root / "configs/default.yaml"), str(root / "configs/local.yaml")],
    )
    parser.add_argument("--backbone", choices=["resnet18", "vit_b16"], default=None)
    args = parser.parse_args()
    cfg = load_config(*args.config)
    build(cfg, backbone=args.backbone)


if __name__ == "__main__":
    main()
