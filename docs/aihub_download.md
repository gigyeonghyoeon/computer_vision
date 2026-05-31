# AI Hub aihubshell 다운로드 설정

## key 종류 (헷갈리기 쉬움)

| 이름 | 예 | 용도 |
|------|-----|------|
| **filekey** | 49825, 53599 | `-filekey` — zip **파일 하나** |
| **datasetkey** | `aihubshell -mode l` 목록 숫자 | `-datasetkey` — **데이터셋** |
| **apikey** | AI Hub 마이페이지 API 키 | `-aihubapikey` (필요 시) |

## datasetkey 확인 (EC2)

```bash
aihubshell -mode l
```

목록에서 찾기:

- `171, 이상행동 CCTV 영상` → `dataset_keys.anomaly`
- `477, 공원 ...` → `dataset_keys.park_normal`
- `489, 유동 인구 ...` → `dataset_keys.pedestrian_cctv`

`configs/aihub_keys.yaml` 상단:

```yaml
dataset_keys:
  anomaly: 171
  park_normal: 477
  pedestrian_cctv: 489
```

## 수동 다운로드 테스트 (1개 파일)

```bash
cd ~/computer_vision
mkdir -p data/raw/test && cd data/raw/test
aihubshell -mode d -datasetkey 477 -filekey 53599
```

> aihubshell v25에는 `-o`/`-localdir` 없음. **다운로드 받을 폴더로 cd 한 뒤** 실행.

## 스크립트

```bash
python scripts/download_aihub.py --dry-run
python scripts/download_aihub.py
```

옵션: `-filekey`, `-datasetkey`, `-aihubapikey`  
저장 위치 = **명령 실행 디렉터리** (스크립트가 dest 폴더에서 실행)
