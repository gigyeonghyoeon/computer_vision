"""모델 평가 — val threshold 설정 → test 영상 단위 평가."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from src.eval.metrics import (
    compute_metrics,
    save_confusion_matrix,
    save_roc_curve,
    save_score_histogram,
)
from src.eval.scoring import aggregate_video_scores, threshold_from_normal
from src.models.autoencoder import AutoEncoder
from src.models.patchcore import PatchCore
from src.preprocess.dataset import FrameDataset
from src.utils.config import get_device, load_config, project_root
from src.utils.seed import set_seed


@torch.no_grad()
def score_autoencoder(
    model: AutoEncoder,
    loader: DataLoader,
    device: str,
) -> list[dict]:
    model.eval()
    results: list[dict] = []
    for batch in loader:
        x = batch["image"].to(device)
        recon, _ = model(x)
        scores = AutoEncoder.reconstruction_error(x, recon)
        for i in range(x.size(0)):
            results.append(
                {
                    "score": float(scores[i].item()),
                    "video_id": batch["video_id"][i],
                    "label": int(batch["label"][i].item()),
                }
            )
    return results


def evaluate(cfg: dict, model_type: str, backbone: str | None = None) -> dict:
    set_seed(cfg["project"]["seed"])
    device = get_device(cfg)
    paths = cfg["paths"]
    eval_cfg = cfg["evaluation"]
    agg = eval_cfg["aggregation"]

    def make_loader(split: str) -> DataLoader:
        ds = FrameDataset(
            paths["metadata_csv"],
            split=split,
            image_size=cfg["preprocess"]["image_size"],
        )
        return DataLoader(ds, batch_size=cfg["patchcore"]["batch_size"], shuffle=False)

    # --- score frames ---
    if model_type == "autoencoder":
        ckpt = torch.load(
            Path(paths["output_dir"]) / "autoencoder" / "best.pt",
            map_location=device,
            weights_only=False,
        )
        model = AutoEncoder(latent_dim=ckpt["cfg"]["latent_dim"]).to(device)
        model.load_state_dict(ckpt["model"])
        score_fn = lambda loader: score_autoencoder(model, loader, device)
        tag = "autoencoder"
        result_subdir = "autoencoder"
    elif model_type == "patchcore":
        bb = backbone or cfg["patchcore"]["backbone"]
        pc = PatchCore.load(
            Path(paths["output_dir"]) / "patchcore" / f"{bb}_memory.pkl",
            device=device,
        )
        score_fn = pc.score_frames
        tag = f"patchcore_{bb}"
        result_subdir = tag
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    out_dir = Path(paths["output_dir"]) / "results" / result_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    val_frames = score_fn(make_loader("val"))
    test_frames = score_fn(make_loader("test"))

    val_videos = aggregate_video_scores(
        [r for r in val_frames if r["label"] == 0], method=agg
    )
    test_videos = aggregate_video_scores(test_frames, method=agg)

    threshold = threshold_from_normal(
        val_videos["score"].values,
        percentile=eval_cfg["threshold_percentile"],
    )

    y_true = test_videos["label"].values
    y_score = test_videos["score"].values
    metrics = compute_metrics(y_true, y_score, threshold)

    save_confusion_matrix(y_true, y_score, threshold, out_dir / "confusion_matrix.png", tag)
    save_score_histogram(y_true, y_score, threshold, out_dir / "score_histogram.png", tag)
    if len(np.unique(y_true)) > 1:
        save_roc_curve(y_true, y_score, out_dir / "roc_curve.png")

    test_videos["pred"] = (y_score >= threshold).astype(int)
    test_videos.to_csv(out_dir / "video_scores.csv", index=False)

    report = {"model": tag, "aggregation": agg, **metrics}
    with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Evaluate anomaly detection model")
    parser.add_argument(
        "--config",
        nargs="+",
        default=[str(root / "configs/default.yaml"), str(root / "configs/local.yaml")],
    )
    parser.add_argument(
        "--model",
        choices=["autoencoder", "patchcore"],
        required=True,
    )
    parser.add_argument("--backbone", choices=["resnet18", "vit_b16"], default=None)
    args = parser.parse_args()
    cfg = load_config(*args.config)
    evaluate(cfg, args.model, backbone=args.backbone)


if __name__ == "__main__":
    main()
