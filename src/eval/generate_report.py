"""3개 모델 결과 비교 + domain gap 한계 정리 리포트 생성."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.config import project_root

MODEL_DIRS = [
    ("AutoEncoder", "autoencoder"),
    ("PatchCore-ResNet18", "patchcore_resnet18"),
    ("PatchCore-ViT", "patchcore_vit_b16"),
]

DOMAIN_GAP_NOTES = """
## Domain Gap 한계

1. **장면 차이:** 공원 정상(야외 CCTV) vs AI Hub 이상행동(실내/거리 등) — 촬영 환경 불일치
2. **유동인구 데이터:** 상권 장면, 이상 라벨 없음 — 학습 보조용으로만 사용
3. **클래스 불균형:** 정상 vs 이상 영상 수 불균형 — AUROC를 주 지표로 해석
4. **연출 데이터:** AI Hub 일부 영상은 연출 수집 — 실제 CCTV와 차이 존재

## 향후 개선

- 정상 CCTV 데이터로 Memory Bank 보강 (fine-tuning)
- 영상 집계 방식 ablation (max vs percentile_95)
- UCF-Crime 등 CCTV-like 정상 클립 추가
"""


def collect_metrics(results_dir: Path) -> pd.DataFrame:
    rows = []
    for name, subdir in MODEL_DIRS:
        path = results_dir / subdir / "metrics.json"
        if not path.exists():
            # fallback: patchcore without backbone suffix
            alt = results_dir / subdir.replace("_resnet18", "").replace("_vit_b16", "") / "metrics.json"
            path = path if path.exists() else alt
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
        rows.append(
            {
                "model": name,
                "auroc": m.get("auroc"),
                "accuracy": m.get("accuracy"),
                "precision": m.get("precision"),
                "recall": m.get("recall"),
                "f1": m.get("f1"),
                "threshold": m.get("threshold"),
            }
        )
    return pd.DataFrame(rows)


def save_comparison_chart(df: pd.DataFrame, out_path: Path) -> None:
    if df.empty:
        return
    metrics = ["auroc", "f1", "precision", "recall", "accuracy"]
    x = range(len(df))
    width = 0.15
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, m in enumerate(metrics):
        ax.bar([xi + i * width for xi in x], df[m], width, label=m.upper())
    ax.set_xticks([xi + width * 2 for xi in x])
    ax.set_xticklabels(df["model"], rotation=15)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison")
    ax.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def generate_report(results_dir: Path, out_dir: Path) -> Path:
    df = collect_metrics(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "eval_report.md"
    lines = [
        "# 이상행동 탐지 실험 결과 리포트",
        "",
        f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 모델 비교",
        "",
    ]
    if df.empty:
        lines.append("_아직 metrics.json 없음. evaluate 스크립트 실행 후 재생성._")
    else:
        lines.append("| " + " | ".join(df.columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
        for _, row in df.iterrows():
            cells = [f"{row[c]:.4f}" if isinstance(row[c], float) else str(row[c]) for c in df.columns]
            lines.append("| " + " | ".join(cells) + " |")
        lines.extend(["", "## 시각화", "", "- `model_comparison.png`", ""])
        save_comparison_chart(df, out_dir / "model_comparison.png")
        df.to_csv(out_dir / "comparison.csv", index=False)

    lines.append(DOMAIN_GAP_NOTES.strip())
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report saved: {md_path}")
    return md_path


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Generate evaluation comparison report")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=root / "outputs/results",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "outputs/reports",
    )
    args = parser.parse_args()
    generate_report(args.results_dir, args.output_dir)


if __name__ == "__main__":
    main()
