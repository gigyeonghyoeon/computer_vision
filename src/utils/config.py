from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(*paths: str | Path) -> dict[str, Any]:
    """여러 YAML을 순서대로 merge. 뒤쪽이 우선."""
    cfg: dict[str, Any] = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            merged = yaml.safe_load(f) or {}
        cfg = _deep_merge(cfg, merged)
    return resolve_paths(cfg)


def resolve_paths(cfg: dict[str, Any]) -> dict[str, Any]:
    root = project_root()
    paths = cfg.get("paths", {})
    for key, value in paths.items():
        p = Path(value)
        if not p.is_absolute():
            paths[key] = str(root / p)
    cfg["paths"] = paths
    return cfg


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def get_device(cfg: dict[str, Any]) -> str:
    import torch

    preferred = cfg.get("project", {}).get("device", "cuda")
    if preferred == "cuda" and torch.cuda.is_available():
        return "cuda"
    return "cpu"
