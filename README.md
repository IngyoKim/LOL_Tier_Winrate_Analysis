# 📘 LOL Tier Winrate Analysis: 티어별 경기 흐름 및 승률 분석 프로젝트

[![GitHub Stars](https://img.shields.io/github/stars/IngyoKim/LOL_Tier_Winrate_Analysis?style=social)](https://github.com/IngyoKim/LOL_Tier_Winrate_Analysis)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

Riot Games 공식 API 기반 대규모 매치 수집 및 타임라인 분석을 통해 리그 오브 레전드 솔로 랭크의 티어별 경기 흐름과 승률에 미치는 영향을 정량적으로 분석하는 프로젝트입니다. 단순 지표 분석을 넘어, **머신러닝 기반의 Objective Score**를 정의하여 경기 중 특정 시점의 종합적인 우위 상태를 하나의 수치로 표현합니다.

---

### 🎯 프로젝트 목표

* **Riot API 기반** 대규모 티어별 경기 데이터 자동 수집
* 타임라인 데이터를 활용한 **시간 흐름 기반 승률 분석**
* 개별 지표를 통합한 **머신러닝 기반 종합 경기 상태 지표 (Objective Score) 정의**
* 티어 간 비교 분석을 통해 지표 구조의 **보편성 검증**
* e스포츠 관전 및 해설에 활용 가능한 **정량적 분석 프레임워크** 제시

### 🔍 데이터 수집 개요

| 항목 | 상세 내용 |
| :--- | :--- |
| **데이터 출처** | Riot Games 공식 [Riot API](https://developer.riotgames.com/) |
| **대상 서버** | KR (한국 서버) 솔로 랭크 |
| **수집 티어** | IRON ~ CHALLENGER (**전체 티어**) |
| **수집 데이터** | **Match Data:** 승패, 라인, 챔피언, 경기 시간<br>**Timeline Data (1분 단위):** Gold, Kill, Dragon, Elder, Baron, Herald, Atakhan, Grub, Towers, Inhibitor |
| **지표 정의** | 모든 분석 지표는 **`team100 (블루) − team200 (레드)`** 기준의 **차이값 (`Diff`)**으로 정의됩니다. |

### 🧠 머신러닝 & Objective Score

본 프로젝트는 지표의 상대적 중요도를 객관적으로 반영하기 위해 로지스틱 회귀 모델을 사용했습니다.

| 모델 상세 | 내용 |
| :--- | :--- |
| **분석 모델** | Logistic Regression (이진 분류) |
| **입력 변수** | `goldDiff`, `totalKillDiff`, `dragonDiff`, `baronDiff`, `heraldDiff`, `elderDiff`, `atakhanDiff`, `grubDiff`, `outerTowerDiff`, `innerTowerDiff`, `baseTowerDiff` |
| **예측 정확도** | 약 **70%** (정량 지표만을 사용한 분석임을 고려할 때 유의미한 결과) |

#### Objective Score 정의

Objective Score는 단순 합산이 아닌, 머신러닝 모델이 학습한 계수(가중치)를 활용하여 계산됩니다.

$$\text{Objective Score} = \sum_{i} \left( \text{Difference}_i \times \text{Weight}_i \right)$$

* **특징:** 머신러닝 모델의 계수를 활용한 **데이터 기반 종합 경기 상태 지표**로, 특정 시점에서 "블루 팀이 얼마나 유리한가"를 하나의 수치로 표현합니다.

### 📊 주요 분석 결과

| 분석 항목 | 결과 및 시사점 |
| :--- | :--- |
| **개별 지표 분석** | Gold Diff가 승패에 가장 **지배적인 영향**을 미치며, 오브젝트 및 타워 차이는 장기적인 주도권 확보를 반영합니다. |
| **Objective Score 분석** | Score 증가에 따라 승률이 **단조 증가**하는 명확한 패턴 확인. 경기 시간 자체보다 **종합 지표 우위**가 승패에 더 직접적인 영향을 미칩니다. |
| **티어별 비교** | 모든 티어에서 유사한 승률 패턴 확인. 본 연구의 지표 구조가 티어에 종속되지 않는 **보편적인 경기 구조**를 반영함을 시사합니다. |
2. 아래 블록 (실행 방법, 응용, 한계)
Markdown

---
### ⚙️ 실행 방법

프로젝트를 로컬 환경에서 재현하려면 다음 단계를 따르세요.

#### 1. 저장소 복제 및 환경 설정

```
git clone [https://github.com/IngyoKim/LOL_Tier_Winrate_Analysis.git](https://github.com/IngyoKim/LOL_Tier_Winrate_Analysis.git)
cd LOL_Tier_Winrate_Analysis

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 라이브러리 설치
pip install -r requirements.txt
```
2. API 키 설정
프로젝트 루트 디렉토리에 .env 파일을 생성하고, 발급받은 Riot API Key를 저장합니다.
```
# .env 파일 내용
RIOT_API_KEY=YOUR_RIOT_API_KEY
```

3. 데이터 수집 실행
원하는 티어의 데이터를 수집하거나, 전체 티어 데이터를 수집합니다.

```
# 단일 티어 데이터 수집 예시
python -m src.fetch.collector

# 전체 티어 데이터 자동 수집
python -m src.fetch.all_collector
```

---
### 🔮 응용 및 발전 방향
본 연구의 Objective Score 기반 프레임워크는 실시간 경기 관전 환경에서 다음과 같이 활용될 수 있습니다.

- 실시간 관전 승률 표시: 현재 시점의 예상 승률을 시각적으로 제공하고, 마우스 오버 시 Objective Score 및 지표 차이 근거를 표시.

- 승률 변화 시뮬레이션: 오브젝트 획득 등 특정 이벤트를 클릭 시, 해당 이벤트가 발생했을 때 예상 Objective Score 및 승률이 어떻게 변화하는지 시뮬레이션.

- 분석 확장: 챔피언 특성 반영, 라인별 지표 추가, 시야 점수 기반 맵 장악력 분석 등으로 모델 정교화.

### ⚠️ 분석의 한계
- 정량화 불가능한 요소: 한타 포지셔닝, 스킬 활용의 질, 순간 판단 실수 등 미시적인 플레이 요소 미반영.

- 예측 정확도: 약 70%의 정확도는 수치만으로 설명되지 않는 비정형적 변수의 존재를 시사.

- 데이터 제약: 개인 프로젝트 한계로 인한 40분 이후 장기 경기 데이터 부족 및 Riot API Rate Limit 제약.
