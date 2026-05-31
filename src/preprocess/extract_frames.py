"""OpenCV 기반 영상 → 프레임 추출."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
from tqdm import tqdm

from src.utils.config import load_config, project_root


def extract_frames(
    video_path: Path,
    output_dir: Path,
    fps: float = 1.0,
) -> list[Path]:
    """영상에서 fps 간격으로 프레임 추출. 반환: 저장된 프레임 경로 목록."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    interval = max(int(round(native_fps / fps)), 1)

    saved: list[Path] = []
    frame_idx = 0
    save_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % interval == 0:
            out_path = output_dir / f"frame_{save_idx:06d}.jpg"
            cv2.imwrite(str(out_path), frame)
            saved.append(out_path)
            save_idx += 1
        frame_idx += 1

    cap.release()
    return saved


def extract_directory(
    raw_dir: Path,
    frames_root: Path,
    fps: float = 1.0,
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mkv", ".MP4"),
) -> None:
    """raw_dir 하위 모든 영상에 대해 프레임 추출.

    출력 구조: frames_root/{dataset}/{video_stem}/frame_XXXXXX.jpg
    dataset은 raw_dir 기준 상대 경로의 첫 번째 세그먼트.
    """
    videos = [p for p in raw_dir.rglob("*") if p.suffix in extensions]
    if not videos:
        print(f"No videos found under {raw_dir}")
        return

    for video_path in tqdm(videos, desc="Extracting frames"):
        rel = video_path.relative_to(raw_dir)
        dataset = rel.parts[0] if len(rel.parts) > 1 else "default"
        video_id = rel.with_suffix("").as_posix().replace("/", "__")
        out_dir = frames_root / dataset / video_id
        extract_frames(video_path, out_dir, fps=fps)


def main() -> None:
    root = project_root()
    cfg = load_config(root / "configs/default.yaml")
    parser = argparse.ArgumentParser(description="Extract frames from videos")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=root / cfg["paths"]["raw_dir"],
    )
    parser.add_argument(
        "--frames-dir",
        type=Path,
        default=root / cfg["paths"]["frames_dir"],
    )
    parser.add_argument("--fps", type=float, default=cfg["preprocess"]["fps"])
    args = parser.parse_args()

    extract_directory(args.raw_dir, args.frames_dir, fps=args.fps)
    print(f"Done. Frames saved to {args.frames_dir}")


if __name__ == "__main__":
    main()
