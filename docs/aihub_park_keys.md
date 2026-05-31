# 공원 CCTV (#477) — 파일키 참고

## Training

| 구분 | 파일 | 용량 | key | 사용 |
|------|------|------|-----|------|
| 라벨 | TL_행위(정상행위)데이터.zip | 2.93 MB | **53593** | ✅ download |
| 라벨 | TL_행위(불법행위) 1~4 | 4~8 MB | 53589–53592 | ❌ |
| 라벨 | TL_객체(...) | 41.96 MB | 53588 | ❌ |
| 원천 | **TS_행위(정상행위)데이터.zip** | **7.47 GB** | **53599** | ✅ **필수** |
| 원천 | TS_행위(불법행위) 1~4 | 31~64 GB | 53595–53598 | ❌ |
| 원천 | TS_객체(...) | 23.73 GB | 53594 | ❌ (이미지) |

## Validation

| 구분 | 파일 | 용량 | key | 사용 |
|------|------|------|-----|-----|
| 라벨 | VL_행위(불법+정상) | 3.62 MB | 53601 | 선택 |
| 원천 | VS_행위(불법+정상) | 24.05 GB | 53603 | 선택 (정상만 필터) |
| 원천 | VS_객체 | 2.92 GB | 53602 | ❌ |

## 프로젝트에서 받을 것 (기본)

```text
53593  TL_행위(정상행위)   — 라벨
53599  TS_행위(정상행위)   — 정상 mp4 (~7.5 GB)
합계 ≈ 7.5 GB
```

다운로드 후:

```bash
unzip data/raw/downloads/park_normal/training/source_TS_*/**/*.zip
python -m src.preprocess.organize_aihub --source data/raw/downloads/park_normal --dataset park_normal
```

설정: `configs/aihub_keys.yaml` (`download: true` on 53593, 53599)
