# AI Hub CCTV 데이터 3종 (본 프로젝트)

```
data/raw/
├── anomaly/           # ① CCTV 이상행동 (test only, label=1)
├── pedestrian_cctv/   # ② 유동인구 분석 CCTV #489 (train/val, label=0)
└── park_normal/       # ③ 공원 CCTV 정상행위 #477 (train/val/test, label=0)
```

| # | AI Hub 데이터셋 | 폴더 |
|---|----------------|------|
| 1 | CCTV 이상행동 | `anomaly/` |
| 2 | 유동인구 분석 CCTV (489) | `pedestrian_cctv/` |
| 3 | 공원 불법행위 감시 CCTV — **정상행위만** (477) | `park_normal/` |

> 공원 데이터(477)의 **불법행위** 클립은 사용하지 않음.

(선택) UCF101, KTH → `ucf101/`, `kth/` — AI Hub만으로도 실험 가능