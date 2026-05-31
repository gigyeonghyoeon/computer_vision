# Domain Gap 및 실험 한계 (발표·보고서용)

## 1. Domain Gap

| 비교 | 정상 테스트 | 이상 테스트 | 차이 |
|------|-------------|-------------|------|
| 장면 | AI Hub 공원 CCTV | AI Hub 이상행동 CCTV | 실내/거리 vs 공원 |
| 행동 | 산책, 휴식 | 폭행, 절도, 침입 등 | 행동 + 환경 gap |
| 학습 | UCF101/KTH + CCTV | — | 일반 행동 vs CCTV |

→ AUROC/F1은 **순수 행동 이상 탐지**와 **CCTV 도메인 차이**가 섞여 측정됨.

## 2. 데이터 한계

- **유동인구 CCTV:** 상권 장면, 이상 라벨 없음 → 학습 보조만
- **클래스 불균형:** 공원 정상 480클립 vs 이상행동 수천 클립
- **연출 데이터:** AI Hub 일부 영상은 시나리오 연출
- **Accuracy 주의:** 정상 비율 높으면 Accuracy만 높아도 Recall 낮을 수 있음

## 3. 영상 집계 Trade-off

| 집계 | Recall | Precision |
|------|--------|-----------|
| max | 높음 | 낮을 수 있음 |
| percentile_95 | 중간 | 중간 |

## 4. 향후 개선

- 정상 CCTV Memory Bank 보강
- UCF-Crime 이벤트 전 구간 등 CCTV-like 정상 추가
- Grad-CAM / PatchCore heatmap 시각화
