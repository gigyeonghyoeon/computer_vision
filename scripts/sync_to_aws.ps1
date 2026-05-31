# 로컬(Windows) → AWS EC2 동기화
# 사용 전 아래 변수를 본인 EC2 정보로 수정하세요.

$EC2_USER = "ubuntu"
$EC2_HOST = "YOUR_EC2_PUBLIC_IP"
$KEY_PATH = "C:\path\to\your-key.pem"
$REMOTE_DIR = "~/computer_vision"

Write-Host "Syncing code to EC2..."
scp -i $KEY_PATH -r `
  configs `
  src `
  scripts `
  requirements.txt `
  docs `
  "${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/"

Write-Host "Syncing processed data (frames + metadata)..."
scp -i $KEY_PATH -r `
  data/processed `
  "${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/data/"

Write-Host "Done. SSH into EC2 and run:"
Write-Host "  cd $REMOTE_DIR && bash scripts/run_aws_train.sh"
