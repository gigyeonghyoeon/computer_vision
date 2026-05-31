# raw 영상을 아래 구조로 배치하세요 (폴더명 = dataset 키)

```
data/raw/
├── ucf101/          # UCF101 정상 (학습)
├── kth/             # KTH 정상 (학습)
├── park_normal/     # AI Hub 공원 정상행위 (학습/val/test split)
├── pedestrian_cctv/ # AI Hub 유동인구 CCTV (학습/val split, test 정상 X)
└── anomaly/         # AI Hub 이상행동 (test only)
```

각 하위 폴더에 `.mp4` 영상을 넣은 뒤 프레임 추출을 실행합니다.
