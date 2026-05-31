# 데이터 준비 가이드

로컬에서 다운로드·정리·전처리 → AWS로 `data/processed` 동기화.

---

## 1. 폴더 생성

```powershell
cd c:\Users\rlrud\project\computer_vision
python -m src.preprocess.setup_dirs
```

생성되는 구조:

```text
data/raw/
├── ucf101/
├── kth/
├── park_normal/
├── pedestrian_cctv/
└── anomaly/
```

---

## 2. AI Hub 다운로드 (aihubshell)

1. [AI Hub](https://www.aihub.or.kr) 가입·로그인
2. 데이터셋 이용신청 (승인 대기)
3. [aihubshell](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=data&dataSetSn=714) 설치
4. 마이페이지에서 **dataset key** 확인

| 용도 | AI Hub 데이터셋 | dataSetSn | 저장 폴더 |
|------|-----------------|-----------|-----------|
| CCTV 정상 (공원) | [공원 주요시설 및 불법행위 감시 CCTV](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=477) | 477 | `park_normal/` |
| CCTV 정상 (상권) | [유동인구 분석 CCTV](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=489) | 489 | `pedestrian_cctv/` |
| CCTV 이상 | 주거 및 공용공간 이상행동 등 (과제에서 지정한 데이터셋) | 515 등 | `anomaly/` |

```powershell
# Windows — dataset key는 마이페이지에서 확인
aihubshell -mode d -datasetkey <KEY> -localdir data\raw\downloads\park
aihubshell -mode d -datasetkey <KEY> -localdir data\raw\downloads\pedestrian
aihubshell -mode d -datasetkey <KEY> -localdir data\raw\downloads\anomaly
```

> 용량이 크면 **EC2에서 aihubshell**로 받고, 정리 후 processed만 로컬로 받아도 됩니다.

---

## 3. AI Hub → 프로젝트 폴더 정리

다운로드 압축 해제 후 **정상행위만** 분리:

```powershell
# 공원: 정상행위 mp4 → park_normal/
python -m src.preprocess.organize_aihub --source data/raw/downloads/park --dataset park_normal

# 유동인구: 전체 mp4 → pedestrian_cctv/
python -m src.preprocess.organize_aihub --source data/raw/downloads/pedestrian --dataset pedestrian_cctv

# 이상행동: mp4 → anomaly/
python -m src.preprocess.organize_aihub --source data/raw/downloads/anomaly --dataset anomaly
```

`organize_aihub`는 경로에 `정상`, `normal`, `불법`, `illegal` 등 키워드가 있으면 자동 필터링합니다.

---

## 4. UCF101 / KTH

| 데이터 | URL | 배치 |
|--------|-----|------|
| UCF101 | https://www.crcv.ucf.edu/projects/data/UCF101.php | `data/raw/ucf101/<클래스명>/*.avi` |
| KTH | https://www.csc.kth.se/cvap/actions/ | `data/raw/kth/<person>_<scenario>/*.avi` |

**UCF101 사용 클래스** → `configs/normal_classes.yaml` 참고  
(Typing, WalkingWithDog, Haircut 등 9개)

**KTH:** walking, jogging, running, boxing, handclapping, handwaving

---

## 5. 전처리 (로컬)

```powershell
python -m src.preprocess.extract_frames
python -m src.preprocess.build_metadata
python -m src.preprocess.validate_split
```

확인:

```text
data/processed/
├── frames/
│   ├── park_normal/...
│   ├── anomaly/...
│   └── ...
└── metadata.csv
```

---

## 6. AWS 동기화

`scripts/sync_to_aws.ps1`에서 EC2 IP·키 경로 수정 후:

```powershell
.\scripts\sync_to_aws.ps1
```

EC2에서:

```bash
cd ~/computer_vision
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_aws_train.sh
```

---

## 7. 체크리스트

- [ ] AI Hub 이용신청 승인
- [ ] `park_normal` — **정상행위만** 포함 (불법행위 제외)
- [ ] `anomaly` — 이상행동만, train에 섞이지 않음
- [ ] UCF101/KTH 클래스 선정 (`normal_classes.yaml`)
- [ ] `metadata.csv` split 확인 (`validate_split`)
- [ ] `data/processed` AWS sync

---

## 용량 참고

| 데이터 | 대략적 규모 |
|--------|-------------|
| 공원 정상 | ~10시간 (480클립) |
| 유동인구 | ~330시간 (선택 다운로드 가능) |
| 이상행동 | 데이터셋별 상이 |
| UCF101 | ~6.5GB |
| KTH | ~1GB |

처음에는 **공원 정상 + 이상행동 소량 + UCF101 일부**만으로 파이프라인 검증 후 전체 확장을 권장합니다.
