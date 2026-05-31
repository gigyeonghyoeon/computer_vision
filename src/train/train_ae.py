"""AutoEncoder 학습."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from src.models.autoencoder import AutoEncoder
from src.preprocess.dataset import FrameDataset
from src.utils.config import get_device, load_config, project_root
from src.utils.seed import set_seed


def train(cfg: dict) -> Path:
    set_seed(cfg["project"]["seed"])
    device = get_device(cfg)
    ae_cfg = cfg["autoencoder"]
    paths = cfg["paths"]

    dataset = FrameDataset(
        paths["metadata_csv"],
        split="train",
        train_normal_only=True,
        image_size=cfg["preprocess"]["image_size"],
        train=True,
    )
    loader = DataLoader(
        dataset,
        batch_size=ae_cfg["batch_size"],
        shuffle=True,
        num_workers=0,
        pin_memory=device == "cuda",
    )

    model = AutoEncoder(latent_dim=ae_cfg["latent_dim"]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=ae_cfg["lr"])
    criterion = torch.nn.MSELoss()

    out_dir = Path(paths["output_dir"]) / "autoencoder"
    out_dir.mkdir(parents=True, exist_ok=True)
    best_loss = float("inf")
    patience = ae_cfg["early_stop_patience"]
    stale = 0

    for epoch in range(1, ae_cfg["epochs"] + 1):
        model.train()
        total_loss = 0.0
        for batch in loader:
            x = batch["image"].to(device)
            recon, _ = model(x)
            loss = criterion(recon, x)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * x.size(0)

        avg_loss = total_loss / len(dataset)
        print(f"Epoch {epoch}/{ae_cfg['epochs']}  loss={avg_loss:.6f}")

        if avg_loss < best_loss:
            best_loss = avg_loss
            stale = 0
            ckpt = out_dir / "best.pt"
            torch.save({"model": model.state_dict(), "cfg": ae_cfg}, ckpt)
        else:
            stale += 1
            if stale >= patience:
                print(f"Early stop at epoch {epoch}")
                break

    print(f"Saved to {out_dir / 'best.pt'}")
    return out_dir / "best.pt"


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Train AutoEncoder on normal data")
    parser.add_argument(
        "--config",
        nargs="+",
        default=[str(root / "configs/default.yaml"), str(root / "configs/local.yaml")],
        help="YAML configs (later overrides earlier). Use configs/aws.yaml on EC2.",
    )
    args = parser.parse_args()
    cfg = load_config(*args.config)
    train(cfg)


if __name__ == "__main__":
    main()
