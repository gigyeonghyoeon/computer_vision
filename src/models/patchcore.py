"""PatchCore anomaly detector — ResNet18 / ViT backbone."""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.neighbors import NearestNeighbors
from torch.utils.data import DataLoader
from torchvision import models
from tqdm import tqdm

try:
    import timm
except ImportError:
    timm = None


class FeatureExtractor(torch.nn.Module):
    """Backbone에서 patch-level feature 추출."""

    def __init__(self, backbone: str = "resnet18"):
        super().__init__()
        self.backbone_name = backbone
        self.features: dict[str, torch.Tensor] = {}

        if backbone == "resnet18":
            net = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            self.model = torch.nn.Sequential(*list(net.children())[:-2])
            self.model.eval()
            self._hook_layer2_layer3(net)
        elif backbone == "vit_b16":
            if timm is None:
                raise ImportError("timm required for ViT backbone")
            self.model = timm.create_model(
                "vit_base_patch16_224", pretrained=True, num_classes=0
            )
            self.model.eval()
        else:
            raise ValueError(f"Unknown backbone: {backbone}")

    def _hook_layer2_layer3(self, net: torch.nn.Module) -> None:
        def hook(name):
            def fn(_m, _i, out):
                self.features[name] = out

            return fn

        net.layer2.register_forward_hook(hook("layer2"))
        net.layer3.register_forward_hook(hook("layer3"))

    @torch.no_grad()
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.backbone_name == "resnet18":
            _ = self.model(x)
            f2 = self.features["layer2"]
            f3 = self.features["layer3"]
            f2 = F.interpolate(f2, size=f3.shape[-2:], mode="bilinear", align_corners=False)
            feat = torch.cat([f2, f3], dim=1)  # (B, C, H, W)
            return feat
        # ViT: patch tokens (exclude cls)
        feat = self.model.forward_features(x)
        if feat.ndim == 3:
            feat = feat[:, 1:, :]  # (B, N, D)
            b, n, d = feat.shape
            side = int(n**0.5)
            feat = feat.transpose(1, 2).reshape(b, d, side, side)
        return feat


def _patchify(feat: torch.Tensor) -> np.ndarray:
    """(B, C, H, W) → (B*H*W, C) numpy."""
    b, c, h, w = feat.shape
    patches = feat.permute(0, 2, 3, 1).reshape(b * h * w, c)
    return patches.cpu().numpy()


class PatchCore:
    def __init__(
        self,
        backbone: str = "resnet18",
        coreset_ratio: float = 0.1,
        k_neighbors: int = 9,
        device: str = "cpu",
    ):
        self.backbone = backbone
        self.coreset_ratio = coreset_ratio
        self.k_neighbors = k_neighbors
        self.device = device
        self.extractor = FeatureExtractor(backbone).to(device)
        self.extractor.eval()
        self.memory_bank: np.ndarray | None = None
        self.knn: NearestNeighbors | None = None

    @torch.no_grad()
    def _collect_features(self, loader: DataLoader) -> np.ndarray:
        all_patches: list[np.ndarray] = []
        for batch in tqdm(loader, desc="Extracting features"):
            imgs = batch["image"].to(self.device)
            feat = self.extractor(imgs)
            all_patches.append(_patchify(feat))
        return np.concatenate(all_patches, axis=0)

    def _coreset_subsample(self, features: np.ndarray) -> np.ndarray:
        n = len(features)
        k = max(int(n * self.coreset_ratio), self.k_neighbors + 1)
        k = min(k, n)
        rng = np.random.default_rng(42)
        idx = rng.choice(n, size=k, replace=False)
        return features[idx]

    def fit(self, loader: DataLoader) -> None:
        features = self._collect_features(loader)
        self.memory_bank = self._coreset_subsample(features)
        self.knn = NearestNeighbors(n_neighbors=self.k_neighbors, metric="euclidean")
        self.knn.fit(self.memory_bank)
        print(f"Memory bank: {self.memory_bank.shape[0]} patches")

    @torch.no_grad()
    def score_frames(self, loader: DataLoader) -> list[dict]:
        """프레임별 anomaly score (patch kNN max distance)."""
        assert self.knn is not None
        results: list[dict] = []

        for batch in tqdm(loader, desc="Scoring"):
            imgs = batch["image"].to(self.device)
            feat = self.extractor(imgs)
            patches = _patchify(feat)
            dists, _ = self.knn.kneighbors(patches)
            patch_scores = dists[:, -1]  # k-th neighbor distance

            b, _, h, w = feat.shape
            n_patches = h * w
            for i in range(b):
                start = i * n_patches
                end = start + n_patches
                frame_score = float(patch_scores[start:end].max())
                results.append(
                    {
                        "score": frame_score,
                        "video_id": batch["video_id"][i],
                        "label": int(batch["label"][i].item()),
                    }
                )
        return results

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "backbone": self.backbone,
                    "coreset_ratio": self.coreset_ratio,
                    "k_neighbors": self.k_neighbors,
                    "memory_bank": self.memory_bank,
                },
                f,
            )

    @classmethod
    def load(cls, path: str | Path, device: str = "cpu") -> "PatchCore":
        with open(path, "rb") as f:
            data = pickle.load(f)
        model = cls(
            backbone=data["backbone"],
            coreset_ratio=data["coreset_ratio"],
            k_neighbors=data["k_neighbors"],
            device=device,
        )
        model.memory_bank = data["memory_bank"]
        model.knn = NearestNeighbors(n_neighbors=model.k_neighbors, metric="euclidean")
        model.knn.fit(model.memory_bank)
        return model
