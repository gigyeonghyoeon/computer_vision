#!/usr/bin/env bash
# AI Hub 데이터 다운로드 템플릿 (EC2 또는 로컬)
# AI Hub 마이페이지에서 dataset key 확인 후 사용

set -euo pipefail
LOCAL_DIR="${1:-./data/raw}"

# 예시 — AI Hub 페이지의 dataset key로 교체
# DATASET_KEY_PARK=71706
# DATASET_KEY_PEDESTRIAN=489
# DATASET_KEY_ANOMALY=YOUR_KEY

echo "aihubshell download template"
echo "Local dir: $LOCAL_DIR"
echo ""
echo "Usage:"
echo "  aihubshell -mode d -datasetkey <KEY> -localdir $LOCAL_DIR/park_normal"
echo "  aihubshell -mode d -datasetkey <KEY> -localdir $LOCAL_DIR/pedestrian_cctv"
echo "  aihubshell -mode d -datasetkey <KEY> -localdir $LOCAL_DIR/anomaly"
echo ""
echo "Download 후 data/raw/README.md 구조에 맞게 폴더 정리"
