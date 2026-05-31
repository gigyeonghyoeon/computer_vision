"""프레임 score → 영상 score 집계 + threshold."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd


def aggregate_video_scores(
    frame_results: list[dict],
    method: str = "max",
) -> pd.DataFrame:
    """프레임별 score를 video_id 단위로 집계."""
    by_video: dict[str, list[float]] = defaultdict(list)
    labels: dict[str, int] = {}

    for r in frame_results:
        vid = r["video_id"]
        by_video[vid].append(r["score"])
        labels[vid] = r["label"]

    rows = []
    for vid, scores in by_video.items():
        arr = np.array(scores)
        if method == "max":
            video_score = float(arr.max())
        elif method == "percentile_95":
            video_score = float(np.percentile(arr, 95))
        else:
            raise ValueError(f"Unknown aggregation: {method}")

        rows.append({"video_id": vid, "score": video_score, "label": labels[vid]})

    return pd.DataFrame(rows)


def threshold_from_normal(scores: np.ndarray, percentile: float = 95.0) -> float:
    """정상(val) score 분포의 percentile을 임계값으로."""
    return float(np.percentile(scores, percentile))
