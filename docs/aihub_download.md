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

- `19. 이상행동CCTV` → 숫자를 `dataset_keys.anomaly` 에
- `173. 공원 ...` → `dataset_keys.park_normal`
- `154. 유동인구 ...` → `dataset_keys.pedestrian_cctv`

`configs/aihub_keys.yaml` 상단:

```yaml
dataset_keys:
  anomaly: 12345
  park_normal: 67890
  pedestrian_cctv: 11111
```

## 수동 다운로드 테스트 (1개 파일)

```bash
cd ~/computer_vision
mkdir -p data/raw/test
aihubshell -mode d -datasetkey <DATASETKEY> -filekey 53599 -o data/raw/test
```

## 스크립트

```bash
python scripts/download_aihub.py --dry-run
python scripts/download_aihub.py
```

v25+ 옵션: `-o` (저장 경로), `-filekey`, `-datasetkey`  
(`-localdir` 은 사용 안 함)
