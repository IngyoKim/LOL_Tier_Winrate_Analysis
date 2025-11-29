import os
import time
import pandas as pd

from src.utils.riot_api import (
    fetch_players_by_tier,
    fetch_match_ids,
    fetch_match_info,
    fetch_match_timeline,       # << 추가됨
    extract_match_rows,
    extract_timeline_features,
)

TIER_MAP = {
    "C": "CHALLENGER",
    "GM": "GRANDMASTER",
    "M": "MASTER",
    "D": "DIAMOND",
    "E": "EMERALD",
    "P": "PLATINUM",
    "G": "GOLD",
    "S": "SILVER",
    "B": "BRONZE",
    "I": "IRON",
}

HIGH_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]


# -----------------------------------------------------------
# 1) PUUID 수집
# -----------------------------------------------------------
def collect_puuids(tier: str, division: str | None, target_count: int):
    print("===================================================")
    print(f"▶ PUUID 수집 시작: {tier} {division or ''} / 목표 {target_count}명")
    print("===================================================\n")

    os.makedirs("data/raw", exist_ok=True)

    puuids = []
    page = 1

    while len(puuids) < target_count:
        print(f"  - 페이지 요청: page {page}")
        players = fetch_players_by_tier(tier, division, page)

        if not players:
            print("  - 더 이상 데이터 없음.\n")
            break

        print(f"  - 불러온 플레이어 수: {len(players)}명")

        for p in players:
            if "puuid" in p:
                puuids.append(p["puuid"])

        if tier in HIGH_TIERS:
            break

        page += 1
        time.sleep(1.0)

    puuids = list(set(puuids))[:target_count]

    filename = f"{tier}_{division}_puuids.txt" if division else f"{tier}_puuids.txt"
    save_path = f"data/raw/{filename}"

    with open(save_path, "w") as f:
        f.writelines(p + "\n" for p in puuids)

    print("\n===================================================")
    print(f"✔ PUUID 수집 완료: 총 {len(puuids)}명")
    print(f"✔ 저장 완료 → {save_path}")
    print("===================================================\n")

    return puuids, filename.replace("_puuids.txt", "")


# -----------------------------------------------------------
# 2) Match 정보 수집 (finish + timeline)
# -----------------------------------------------------------
def collect_matches_from_puuids(puuids, tier_name, match_per_player):
    print("===================================================")
    print(f"▶ Match 정보 수집 시작: {tier_name}")
    print(f"▶ 대상 PUUID 수: {len(puuids)}명")
    print("===================================================\n")

    os.makedirs("data/processed", exist_ok=True)

    finish_rows = []
    timeline_rows = []
    seen = set()

    total_players = len(puuids)

    for idx, puuid in enumerate(puuids, 1):
        print(f"[{idx}/{total_players}] PUUID 처리 중 → {puuid[:12]}...")

        match_ids = fetch_match_ids(puuid, match_per_player)
        print(f"  - 가져온 matchId: {len(match_ids)}개")
        time.sleep(3)

        for m in match_ids:
            if m in seen:
                continue
            seen.add(m)

            print(f"    · match 조회 → {m}")
            match_json = fetch_match_info(m)
            timeline_json = fetch_match_timeline(m)  # << 타임라인 가져오기 추가

            if not match_json or not timeline_json:
                print("      (오류 발생 → 건너뜀)")
                continue

            # --------------------------
            # FINISH 데이터 추출
            # --------------------------
            finish = extract_match_rows(match_json)
            finish_rows.extend(finish)

            # --------------------------
            # TIMELINE 데이터 추출
            # --------------------------
            timeline = extract_timeline_features(match_json, timeline_json)
            timeline_rows.append(timeline)

            time.sleep(1.2)

    # --------------------------
    # CSV 저장
    # --------------------------
    finish_path = f"data/processed/{tier_name}_matches.csv"
    timeline_path = f"data/processed/{tier_name}_timeline.csv"

    pd.DataFrame(finish_rows).to_csv(finish_path, index=False)
    pd.DataFrame(timeline_rows).to_csv(timeline_path, index=False)

    print("\n===================================================")
    print("✔ Match 정보 수집 완료")
    print(f"✔ 총 고유 match: {len(seen)}개")
    print(f"✔ FINISH row 수: {len(finish_rows)}개 → {finish_path}")
    print(f"✔ TIMELINE row 수: {len(timeline_rows)}개 → {timeline_path}")
    print("===================================================\n")

    return finish_path, timeline_path


# -----------------------------------------------------------
# 3) 전체 orchestrator
# -----------------------------------------------------------
def collect_tier_all(tier, division=None, player_count=300, match_per_player=10):
    print("=============================================")
    print("▶ 티어 전체 수집 시작")
    print(f"  - Tier: {tier}")
    print(f"  - Division: {division}")
    print(f"  - Player Count: {player_count}")
    print(f"  - Match Per Player: {match_per_player}")
    print("=============================================\n")

    tier = tier.upper()
    if division:
        division = division.upper()

    # STEP 1 — PUUID 수집
    puuids, tier_name = collect_puuids(tier, division, player_count)

    # STEP 2 — Match(최종 + timeline) 수집
    finish_path, timeline_path = collect_matches_from_puuids(
        puuids, tier_name, match_per_player
    )

    print("=============================================")
    print("🎉 전체 작업 완료")
    print(f"➡ FINISH CSV: {finish_path}")
    print(f"➡ TIMELINE CSV: {timeline_path}")
    print("=============================================")

    return finish_path, timeline_path


# -----------------------------------------------------------
# 4) CLI 실행
# -----------------------------------------------------------
if __name__ == "__main__":
    raw_tier = input("티어 입력(C/GM/M/D/E/P/G/S/B/I): ").upper().strip()
    division = input("디비전 입력(I/II/III/IV 또는 빈칸): ").upper().strip() or None
    player_count = int(input("가져올 플레이어 수: "))
    match_per_player = int(input("플레이어당 경기 수: "))

    # 약어 → 실제 티어 이름 매핑
    if raw_tier in TIER_MAP:
        tier = TIER_MAP[raw_tier]
    else:
        print("잘못된 티어 입력입니다.")
        exit()

    collect_tier_all(tier, division, player_count, match_per_player)