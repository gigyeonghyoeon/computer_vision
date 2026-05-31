"""configs/aihub_keys.yaml 로드 + aihubshell 다운로드.

AI Hub aihubshell: -filekey + -datasetkey (+ -aihubapikey)
저장 경로 옵션 없음 → 대상 폴더에서 실행 (cwd)
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
        hints = {
            "anomaly": ("171", "이상행동 CCTV"),
            "park_normal": ("477", "공원"),
            "pedestrian_cctv": ("489", "유동"),
        }
        mode_l_key, grep_word = hints.get(group, ("?", group))
        raise ValueError(
            f"dataset_keys.{group} 가 비어 있습니다.\n"
            f"  1) aihubshell -mode l | grep {grep_word}\n"
            f"  2) configs/aihub_keys.yaml 의 dataset_keys.{group} 에 숫자 입력\n"
            f"     (예: {mode_l_key})\n"
            f"  3) 확인: aihubshell -mode l -datasetkey {mode_l_key} | head"
        )
    return str(dk)


def _build_cmd(cfg: dict, datasetkey: str, filekey: str) -> list[str]:
    cmd = [
        "aihubshell",
        "-mode",
        "d",
        "-datasetkey",
        datasetkey,
        "-filekey",
        filekey,
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
        cmd = _build_cmd(cfg, datasetkey, filekey)
        label = meta.get("file") or meta.get("name", "")
        print(f"→ datasetkey={datasetkey} filekey={filekey}  dest={dest}  ({label})")
        if dry_run:
            print(f"   cd {dest} && {' '.join(cmd)}")
            continue
        dest.mkdir(parents=True, exist_ok=True)
        subprocess.run(cmd, check=True, cwd=dest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download AI Hub files from aihub_keys.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")
    args = parser.parse_args()
    download_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
