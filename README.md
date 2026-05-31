# CCTV 이상행동 탐지 (AutoEncoder + PatchCore)

AI Hub CCTV 데이터와 PatchCore를 활용한 **영상 단위** 이상행동 탐지 프로젝트.

## 워크플로우: 로컬 개발 + AWS 학습

```text
[로컬 PC]                          [AWS EC2 GPU]
  코드 작성 / 전처리                  본격 학습 / 평가
  소규모 테스트 (local.yaml)          aws.yaml + run_aws_train.sh
       │                                    ▲
       └──── sync_to_aws (코드 + processed) ─┘
```

| 단계 | 어디서 | 명령 |
|------|--------|------|
| 환경 설정 | 로컬 | `pip install -r requirements.txt` |
| 영상 배치 | 로컬 | `data/raw/` (README 참고) |
| 프레임 추출 | 로컬 | `python -m src.preprocess.extract_frames` |
| metadata 생성 | 로컬 | `python -m src.preprocess.build_metadata` |
| 파이프라인 테스트 | 로컬 | `local.yaml` (epoch 2, CPU) |
| EC2 동기화 | 로컬 | `scripts/sync_to_aws.ps1` |
| 학습 + 평가 | **AWS** | `bash scripts/run_aws_train.sh` |
| 결과 다운로드 | 로컬 | `outputs/` scp/rsync |

---

## 1. 로컬 환경 설정

```powershell
cd c:\Users\rlrud\project\computer_vision
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2. 데이터 준비

상세 가이드: **[docs/data_preparation.md](docs/data_preparation.md)**

```powershell
python -m src.preprocess.setup_dirs
# AI Hub: scripts/download_aihub.ps1 (dataset key 입력 후)
```

```text
data/raw/
├── ucf101/
├── kth/
├── park_normal/       # AI Hub 공원 정상행위
├── pedestrian_cctv/   # AI Hub 유동인구 CCTV
└── anomaly/           # AI Hub 이상행동
```

---

## 3. 전처리 (로컬)

```powershell
# 1초당 1프레임 추출
python -m src.preprocess.extract_frames

# metadata.csv 생성 (train/val/test split)
python -m src.preprocess.build_metadata
```

---

## 4. 로컬 smoke test

GPU 없이 파이프라인 동작 확인 (epoch 2, batch 8):

```powershell
python -m src.preprocess.create_smoke_data
python -m src.train.train_ae --config configs/default.yaml configs/local.yaml
python -m src.train.build_memory_bank --config configs/default.yaml configs/local.yaml --backbone resnet18
python -m src.eval.evaluate --config configs/default.yaml configs/local.yaml --model autoencoder
python -m src.eval.evaluate --config configs/default.yaml configs/local.yaml --model patchcore --backbone resnet18
python -m src.eval.generate_report
```

---

## 5. AWS EC2 설정

**권장 인스턴스:** g4dn.xlarge 또는 g5.xlarge (GPU)

```bash
# EC2 접속 후
sudo apt update && sudo apt install -y python3-pip python3-venv
git clone <your-repo> ~/computer_vision   # 또는 sync_to_aws로 업로드
cd ~/computer_vision
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# CUDA 확인
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 6. 로컬 → AWS 동기화

**Windows (PowerShell):** `scripts/sync_to_aws.ps1`에서 EC2 IP, 키 경로 수정 후 실행

**Mac/Linux:**

```bash
EC2_HOST=1.2.3.4 KEY=~/.ssh/key.pem bash scripts/sync_to_aws.sh
```

동기화 대상:
- `configs/`, `src/`, `scripts/`, `requirements.txt`
- `data/processed/` (frames + metadata.csv)
- `data/raw/`는 용량이 크므로 **EC2에서 aihubshell로 직접 다운로드**하거나 processed만 sync

---

## 7. AWS에서 학습

```bash
cd ~/computer_vision
source .venv/bin/activate
bash scripts/run_aws_train.sh
```

개별 실행:

```bash
python -m src.train.train_ae --config configs/default.yaml configs/aws.yaml
python -m src.train.build_memory_bank --config configs/default.yaml configs/aws.yaml --backbone resnet18
python -m src.eval.evaluate --config configs/default.yaml configs/aws.yaml --model patchcore --backbone resnet18
python -m src.train.build_memory_bank --config configs/default.yaml configs/aws.yaml --backbone vit_b16
python -m src.eval.evaluate --config configs/default.yaml configs/aws.yaml --model patchcore --backbone vit_b16
python -m src.eval.evaluate --config configs/default.yaml configs/aws.yaml --model autoencoder
```

결과: `outputs/results/` (metrics.json, confusion matrix, ROC curve)

---

## 8. 결과 다운로드 (로컬)

```powershell
scp -i C:\path\to\key.pem -r ubuntu@EC2_IP:~/computer_vision/outputs ./outputs
```

---

## 프로젝트 구조

```text
computer_vision/
├── configs/
│   ├── default.yaml      # 공통 설정
│   ├── local.yaml        # 로컬 테스트 (CPU, 소규모)
│   └── aws.yaml          # AWS GPU 학습
├── data/
│   ├── raw/              # 원본 영상
│   └── processed/        # frames + metadata.csv
├── src/
│   ├── preprocess/       # extract_frames, build_metadata, dataset
│   ├── models/           # autoencoder, patchcore
│   ├── train/            # train_ae, build_memory_bank
│   └── eval/             # evaluate, metrics
├── scripts/
│   ├── sync_to_aws.ps1   # Windows → EC2
│   ├── sync_to_aws.sh    # Mac/Linux → EC2
│   └── run_aws_train.sh  # EC2 전체 학습
└── outputs/              # 체크포인트, 결과
```

---

## 설정 파일

| 파일 | 용도 |
|------|------|
| `configs/default.yaml` | 공통 (경로, split, 하이퍼파라미터) |
| `configs/local.yaml` | 로컬: `device: cpu`, epoch 2 |
| `configs/aws.yaml` | AWS: `device: cuda`, epoch 50 |

---

## 상세 계획

[docs/project_plan.md](docs/project_plan.md)
