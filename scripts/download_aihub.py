"""configs/aihub_keys.yaml 로드 + aihubshell 다운로드."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_keys(path: Path | None = None) -> dict[str, Any]:
    path = path or project_root() / "configs/aihub_keys.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Copy configs/aihub_keys.example.yaml → aihub_keys.yaml"
        )
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _iter_download_items(cfg: dict) -> list[tuple[str, int | str, dict]]:
    """(category_path, key, meta) 목록."""
    items: list[tuple[str, int | str, dict]] = []

    anomaly = cfg.get("anomaly") or {}
    for action, entries in anomaly.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not entry.get("download") or entry.get("key") in (None, "null", ""):
                continue
            env = entry.get("env", "unknown")
            items.append((f"anomaly/{action}/{env}", entry["key"], entry))

    for name, key_field in [("pedestrian_cctv", "pedestrian_cctv"), ("park_normal", "park_normal")]:
        for entry in cfg.get(key_field) or []:
            if not entry.get("download") or entry.get("key") in (None, "null", ""):
                continue
            split = entry.get("split", "data")
            kind = entry.get("kind", "file")
            fname = entry.get("file", entry.get("name", "data"))
            safe = fname.replace(".zip", "").replace(" ", "_")[:40]
            items.append((f"downloads/{name}/{split}/{kind}_{safe}", entry["key"], entry))

    return items


def download_all(dry_run: bool = False) -> None:
    cfg = load_keys()
    items = _iter_download_items(cfg)
    if not items:
        print("download: true 이고 key가 있는 항목이 없습니다.")
        print("configs/aihub_keys.yaml 에 key를 입력하세요.")
        return

    root = project_root() / "data/raw"
    for dest_rel, key, meta in items:
        dest = root / dest_rel
        cmd = ["aihubshell", "-mode", "d", "-datasetkey", str(key), "-localdir", str(dest)]
        print(f"→ key={key}  dest={dest}  meta={meta.get('file') or meta.get('name', '')}")
        if dry_run:
            print("  ", " ".join(cmd))
            continue
        dest.mkdir(parents=True, exist_ok=True)
        subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download AI Hub files from aihub_keys.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")
    args = parser.parse_args()
    download_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
