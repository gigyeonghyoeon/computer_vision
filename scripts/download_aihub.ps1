# AI Hub dataset key 설정 (마이페이지에서 확인 후 입력)
# https://www.aihub.or.kr → 마이페이지 → 데이터셋 → dataset key

# dataSetSn 참고 (페이지 URL 끝 숫자)
#   477 — 공원 주요시설 및 불법행위 감시 CCTV
#   489 — 유동인구 분석 CCTV
#   515 — 주거 및 공용공간 내 이상행동 (예시)

$DATASET_KEY_PARK = "YOUR_KEY_HERE"
$DATASET_KEY_PEDESTRIAN = "YOUR_KEY_HERE"
$DATASET_KEY_ANOMALY = "YOUR_KEY_HERE"

$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ROOT

# aihubshell 설치 확인
if (-not (Get-Command aihubshell -ErrorAction SilentlyContinue)) {
    Write-Host "aihubshell not found. Install from AI Hub website first."
    Write-Host "https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=714"
    exit 1
}

python -m src.preprocess.setup_dirs

Write-Host "Downloading park CCTV..."
aihubshell -mode d -datasetkey $DATASET_KEY_PARK -localdir "data\raw\downloads\park"

Write-Host "Downloading pedestrian CCTV..."
aihubshell -mode d -datasetkey $DATASET_KEY_PEDESTRIAN -localdir "data\raw\downloads\pedestrian"

Write-Host "Downloading anomaly CCTV..."
aihubshell -mode d -datasetkey $DATASET_KEY_ANOMALY -localdir "data\raw\downloads\anomaly"

Write-Host "Organizing files..."
python -m src.preprocess.organize_aihub --source data/raw/downloads/park --dataset park_normal
python -m src.preprocess.organize_aihub --source data/raw/downloads/pedestrian --dataset pedestrian_cctv
python -m src.preprocess.organize_aihub --source data/raw/downloads/anomaly --dataset anomaly

Write-Host "Done. Next: python -m src.preprocess.extract_frames"
