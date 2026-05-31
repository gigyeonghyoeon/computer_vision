# AI Hub 이상행동 CCTV — 전체 파일키 목록 (참고용, Git에 포함)

| # | 행동 | 환경 | 파일 | GB | key |
|---|------|------|------|-----|-----|
| 01 | 폭행 assault | insidedoor | insidedoor_01.zip | 17.76 | 49825 |
| 01 | 폭행 assault | outsidedoor | outsidedoor_01.zip | 27.43 | 49841 |
| 02 | 싸움 fight | insidedoor | insidedoor_01.zip | 21.19 | 49850 |
| 02 | 싸움 fight | outsidedoor | outsidedoor_01.zip | 28.68 | 49753 |
| 03 | 절도 burglary | insidedoor | insidedoor_01.zip | 23.64 | 49765 |
| 03 | 절도 burglary | outsidedoor | outsidedoor_01.zip | 33.59 | 49772 |
| 04 | 기물파손 vandalism | insidedoor | insidedoor_01.zip | 14.98 | 49782 |
| 04 | 기물파손 vandalism | outsidedoor | outsidedoor_01.zip | 28.70 | 49784 |
| 05 | 실신 swoon | insidedoor | insidedoor_01.zip | 27.19 | 49792 |
| 05 | 실신 swoon | outsidedoor | outsidedoor_01.zip | 27.31 | 49803 |
| 06 | 배회 wander | insidedoor | insidedoor_01.zip | 30.13 | 49703 |
| 06 | 배회 wander | outsidedoor | outsidedoor_01.zip | 30.59 | 49708 |
| 07 | 침입 trespass | outsidedoor | outsidedoor_01.zip | 24.44 | 49718 |
| 08 | 투기 dump | insidedoor | insidedoor_01.zip | 28.97 | 49723 |
| 08 | 투기 dump | outsidedoor | outsidedoor_01.zip | 28.98 | 49728 |
| 09 | 강도 robbery | insidedoor | insidedoor_01.zip | 33.30 | 49735 |
| 09 | 강도 robbery | outsidedoor | outsidedoor_01.zip | 23.75 | 49740 |
| 10 | 데이트폭력 datefight | insidedoor | insidedoor_01.zip | 32.83 | 49744 |
| 10 | 데이트폭력 datefight | outsidedoor | outsidedoor_01.zip | 30.43 | 49658 |
| 11 | 납치 kidnap | insidedoor | insidedoor_01.zip | 2.91 | 49664 |
| 11 | 납치 kidnap | outsidedoor | outsidedoor_01.zip | 21.28 | 49668 |
| 12 | 주취 drunken | insidedoor | insidedoor_01.zip | 29.70 | 49672 |
| 12 | 주취 drunken | outsidedoor | outsidedoor_01.zip | 30.23 | 49683 |

## 100GB EC2 — batch1 (`download: true` in aihub_keys.yaml)

| 행동 | key | GB |
|------|-----|-----|
| 기물파손 insidedoor | 49782 | 14.98 |
| 폭행 insidedoor | 49825 | 17.76 |
| 절도 insidedoor | 49765 | 23.64 |
| 침입 outsidedoor | 49718 | 24.44 |
| **합계** | | **~80.8 GB** |

## batch2 (평가 후 삭제, `download: true`로 바꿔서 실행)

| 행동 | key | GB |
|------|-----|-----|
| 실신 insidedoor | 49792 | 27.19 |
| 싸움 insidedoor | 49850 | 21.19 |
| 납치 insidedoor | 49664 | 2.91 |

실제 key 설정: `configs/aihub_keys.yaml` (Git 제외)
