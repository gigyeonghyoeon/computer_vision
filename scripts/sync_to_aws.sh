#!/usr/bin/env bash
# 로컬(Mac/Linux) → AWS EC2 동기화
# Usage: EC2_HOST=1.2.3.4 KEY=~/.ssh/key.pem bash scripts/sync_to_aws.sh

set -euo pipefail

EC2_USER="${EC2_USER:-ubuntu}"
EC2_HOST="${EC2_HOST:?Set EC2_HOST}"
KEY="${KEY:?Set KEY path to .pem}"
REMOTE_DIR="${REMOTE_DIR:-~/computer_vision}"

rsync -avz -e "ssh -i $KEY" \
  --exclude data/raw \
  --exclude outputs \
  --exclude .venv \
  configs/ src/ scripts/ requirements.txt docs/ \
  "${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/"

rsync -avz -e "ssh -i $KEY" \
  data/processed/ \
  "${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/data/processed/"

echo "Done. SSH: ssh -i $KEY ${EC2_USER}@${EC2_HOST}"
echo "Train:  cd ${REMOTE_DIR} && bash scripts/run_aws_train.sh"
