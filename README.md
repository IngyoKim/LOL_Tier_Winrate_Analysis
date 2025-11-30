# 📘 LOL Tier Winrate Analysis

**Riot API 기반 대규모 자동 매치 수집 + 타임라인 기반 승률 분석 프로젝트**

본 프로젝트는 **Riot API**를 활용하여

티어별 대규모 매치 데이터를 자동으로 수집하고,

수집된 데이터를 기반으로 **각 오브젝트·골드·타워 차이가 승률에 미치는 영향**을 분석하는 Python 기반 시스템입니다.

---

# 🚀 주요 기능

## ✅ 1. 티어별 PUUID 자동 수집

- tier/division 입력 → 원하는 수(예: 100명)만큼 자동 수집
- 저장: `data/raw/<TIER>_<DIV>.txt`

---

## ✅ 2. 매치 리스트 및 매치 정보 자동 수집

- 플레이어 당 최근 솔로랭크 N경기(예: 20) 자동 수집
- 모든 matchId 중복 제거 후 저장
- 저장: `data/processed/<TIER>_<DIV>_matches.csv`

---

## ✅ 3. 타임라인 기반 1분 단위 Diff 생성

1분 단위로 아래 모든 값을 계산합니다:
계산을 블루 팀 - 퍼플 팀으로 계산합니다.

### 📊 Gold/Kill

- `goldDiff_m` 글로벌 골드
- `killDiff_m` 글로벌 킬

### 🐉 Epic Monsters

- `dragonDiff_m` 장로 드래곤을 제외한 드래곤
- `elderDiff_m` 장로 드래곤
- `heraldDiff_m` 전령
- `baronDiff_m` 바론
- `atakhanDiff_m` 아타칸
- `grubDiff_m` 공허 유충

### 🏰 Buildings

- `outerTowerDiff_m` 1차 타워
- `innerTowerDiff_m` 2차 타워
- `baseTowerDiff_m` 억제기 앞 타워
- `nexusTowerDiff_m` 쌍둥이 타워
- `inhibitorDiff_m` 억제기

저장 위치:

`data/processed/<TIER>_<DIV>_timeline.csv`

---

## ✅ 4. 전체 티어 자동 수집 (All Collector)

한 번 실행하면 다음 모든 티어를 순서대로 처리합니다:
IRON → BRONZE → SILVER → GOLD → PLATINUM → EMERALD → DIAMOND → MASTER → GRANDMASTER → CHALLENGER

입력 값:

- 티어당 수집할 플레이어 수
- 플레이어당 수집할 매치 수
- 세부 티어 구분 사용 여부(I, II, III, IV)

---

# 🗂 폴더 구조

```
LOL_Tier_Winrate_Analysis/
├─ src/
│ ├─ fetch/
│ │ ├─ collector.py # 단일 티어 수집기
│ │ ├─ all_collector.py # 전체 티어 자동 수집기
│ │
│ ├─ analysis/
│ │ ├─ graphs/ # 시간 별 그래프 저장
│ │ ├─ gold_analysis.py
│ │ ├─ dragon_analysis.py
│ │ ├─ tower_analysis.py
│ │ ├─ baron_analysis.py
│ │ ├─ grub_analysis.py
│ │ ├─ atakhan_analysis.py
│ │ ├─ herald_analysis.py
│ │ ├─ combined_analysis.py
│ │
│ ├─ utils/
│ │ ├─ riot_api/
│ │ │ ├─ __init__.py
│ │ │ ├─ extract_finish.py
│ │ │ ├─ extract_timeline.py
│ │ │ ├─ matches.py
│ │ │ ├─ players.py
│ │ │ ├─ riot_async.py
│ │ │ ├─ timeline.py
│ │ ├─ __init__.py
│ │
├─ data/
│ ├─ raw/ # PUUID 파일 저장
│ ├─ processed/ # CSV 저장
│
├─ .env # RIOT_API_KEY
└─ README.md
```

---

# ⚙️ 설치 및 실행 방법

## 1. 저장소 clone

```bash
git clone <https://github.com/><YOUR_REPO>/LOL_Tier_Winrate_Analysis.git
cd LOL_Tier_Winrate_Analysis
```

## 2. 가상환경 생성 및 패키지 설치

```
python -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. .env 파일 생성

```
RIOT_API_KEY=YOUR_RIOT_API_KEY
```

https://developer.riotgames.com/ 해당 링크에서 발급 가능하며 24시간 마다 갱신 필요

### 4. 단일 티어 데이터 수집

```
python -m src.fetch.collector
```

### 5. 전체 티어 자동 수집

```
python -m src.fetch.all_collector
```

---

# 📈 가능 분석 예시

## ✔ 승률 분석

- 시간별 골드 차이 vs 승률
- 시간별 킬 차이 vs 승률
- 드래곤/전령/바론/유충/아타칸/장로 차이 vs 승률
- 타워/억제기 차이 vs 승률

## ✔ 타임라인 분석

- 승리팀 vs 패배팀의 평균 골드/킬 궤적
- 오브젝트 선점의 게임 결과 영향
- 스노우볼 가능한 시점 분석

## ✔ 피처 조합 분석

- 10분 골드 + 전령 조합의 승률
- 15분 타워 + 유충 조합의 승률
- early game dominance → 승리 전환율

# 🧪 Known Issues / 주의사항

### 🔑 Riot API Key (중요)

- 개발자 무료 키는 **24시간마다 자동 만료**
- 중간에 `Unknown API key` 오류가 발생하면 새 키로 업데이트 필요

### 🔄 Rate Limit (429)

- 여러 티어에서 대량으로 수집 시 Rate Limit 자주 발생
- 필요 시 delay 값을 늘려야 API 차단 방지 가능