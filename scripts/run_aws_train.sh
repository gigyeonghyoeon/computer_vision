#!/usr/bin/env bash
# AWS EC2에서 전체 학습 파이프라인 실행
# Usage: bash scripts/run_aws_train.sh

set -euo pipefail
cd "$(dirname "$0")/.."

CONFIG="configs/default.yaml configs/aws.yaml"

echo "=== AutoEncoder ==="
python -m src.train.train_ae --config $CONFIG

echo "=== PatchCore ResNet18 ==="
python -m src.train.build_memory_bank --config $CONFIG --backbone resnet18
python -m src.eval.evaluate --config $CONFIG --model patchcore --backbone resnet18

echo "=== PatchCore ViT ==="
python -m src.train.build_memory_bank --config $CONFIG --backbone vit_b16
python -m src.eval.evaluate --config $CONFIG --model patchcore --backbone vit_b16

echo "=== AutoEncoder eval ==="
python -m src.eval.evaluate --config $CONFIG --model autoencoder

echo "=== Report ==="
python -m src.eval.generate_report

echo "Done. Results in outputs/results/  Report in outputs/reports/"
