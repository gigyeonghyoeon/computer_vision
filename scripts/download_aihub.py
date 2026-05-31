"""configs/aihub_keys.yaml 로드 + aihubshell 다운로드.

AI Hub v25+: -filekey (파일키) + -datasetkey (데이터셋키) + -o (저장경로)
마이페이지 key 숫자(49825 등) = filekey
"""

from __future__ import annotations

import argparse
import os
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


def _filekey(entry: dict) -> str | None:
    fk = entry.get("filekey") or entry.get("key")
    if fk in (None, "null", ""):
        return None
    return str(fk)


def _iter_download_items(cfg: dict) -> list[tuple[str, str, str, dict]]:
    """(dest_rel, filekey, dataset_group, meta)"""
    items: list[tuple[str, str, str, dict]] = []

    anomaly = cfg.get("anomaly") or {}
    for action, entries in anomaly.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not entry.get("download"):
                continue
            fk = _filekey(entry)
            if not fk:
                continue
            env = entry.get("env", "unknown")
            items.append((f"anomaly/{action}/{env}", fk, "anomaly", entry))

    for group in ("pedestrian_cctv", "park_normal"):
        for entry in cfg.get(group) or []:
            if not entry.get("download"):
                continue
            fk = _filekey(entry)
            if not fk:
                continue
            split = entry.get("split", "data")
            kind = entry.get("kind", "file")
            fname = entry.get("file", entry.get("name", "data"))
            safe = fname.replace(".zip", "").replace(" ", "_").replace("(", "").replace(")", "")[:40]
            items.append((f"downloads/{group}/{split}/{kind}_{safe}", fk, group, entry))

    return items


def _dataset_key(cfg: dict, group: str, entry: dict) -> str:
    if entry.get("datasetkey"):
        return str(entry["datasetkey"])
    keys = cfg.get("dataset_keys") or {}
    dk = keys.get(group)
    if not dk:
        raise ValueError(
            f"dataset_keys.{group} 가 비어 있습니다.\n"
            f"  aihubshell -mode l  로 데이터셋 번호 확인 후 configs/aihub_keys.yaml 에 입력"
        )
    return str(dk)


def _build_cmd(cfg: dict, datasetkey: str, filekey: str, dest: Path) -> list[str]:
    cmd = [
        "aihubshell",
        "-mode",
        "d",
        "-datasetkey",
        datasetkey,
        "-filekey",
        filekey,
        "-o",
        str(dest),
    ]
    apikey = (cfg.get("aihub") or {}).get("apikey") or os.environ.get("AIHUB_API_KEY")
    if apikey:
        cmd.extend(["-aihubapikey", str(apikey)])
    return cmd


def download_all(dry_run: bool = False) -> None:
    cfg = load_keys()
    items = _iter_download_items(cfg)
    if not items:
        print("download: true 이고 filekey가 있는 항목이 없습니다.")
        return

    root = project_root() / "data/raw"
    for dest_rel, filekey, group, meta in items:
        dest = root / dest_rel
        datasetkey = _dataset_key(cfg, group, meta)
        cmd = _build_cmd(cfg, datasetkey, filekey, dest)
        label = meta.get("file") or meta.get("name", "")
        print(f"→ datasetkey={datasetkey} filekey={filekey}  dest={dest}  ({label})")
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
