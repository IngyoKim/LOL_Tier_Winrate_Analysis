import os
import time
import pandas as pd

from src.utils.riot_api import *

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

        # 진행률 출력
        print(f"  - 불러온 플레이어 수: {len(players)}명")

        for p in players:
            if "puuid" in p:
                puuids.append(p["puuid"])

        # 페이지 증가 (하이 티어는 1페이지만 존재)
        if tier in HIGH_TIERS:
            break
        page += 1

        time.sleep(1.0)

    # 최종 처리
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
# 2) Match 정보 수집
# -----------------------------------------------------------
def collect_matches_from_puuids(puuids, tier_name, match_per_player):
    print("===================================================")
    print(f"▶ Match 정보 수집 시작: {tier_name}")
    print(f"▶ 대상 PUUID 수: {len(puuids)}명")
    print("===================================================\n")

    os.makedirs("data/processed", exist_ok=True)

    output_path = f"data/processed/{tier_name}_matches.csv"

    result_rows = []
    seen = set()

    total_players = len(puuids)

    for idx, puuid in enumerate(puuids, 1):
        print(f"[{idx}/{total_players}] PUUID 처리 중 → {puuid[:12]}...")

        match_ids = fetch_match_ids(puuid, match_per_player)
        print(f"  - 가져온 matchId: {len(match_ids)}개")
        time.sleep(1.2)

        for m in match_ids:
            if m in seen:
                continue
            seen.add(m)

            print(f"    · match 조회 → {m}")
            match_json = fetch_match_info(m)
            if not match_json:
                print("      (오류 발생 → 건너뜀)")
                continue

            rows = extract_match_rows(match_json)
            result_rows.extend(rows)

            time.sleep(1.2)

    pd.DataFrame(result_rows).to_csv(output_path, index=False)

    print("\n===================================================")
    print("✔ Match 정보 수집 완료")
    print(f"✔ 총 고유 match: {len(seen)}개")
    print(f"✔ 총 participant row: {len(result_rows)}개")
    print(f"✔ 저장 완료 → {output_path}")
    print("===================================================\n")

    return output_path


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

    # 1단계: PUUID 수집
    puuids, tier_name = collect_puuids(tier, division, player_count)

    # 2단계: Match 수집
    output_path = collect_matches_from_puuids(puuids, tier_name, match_per_player)

    print("=============================================")
    print("🎉 전체 작업 완료")
    print(f"➡ 결과 파일: {output_path}")
    print("=============================================")

    return output_path


if __name__ == "__main__":
    tier = input("티어 입력: ").upper()
    division = input("디비전 입력(I/II/III/IV 또는 빈칸): ").upper() or None
    player_count = int(input("가져올 플레이어 수: "))
    match_per_player = int(input("플레이어당 경기 수: "))

    collect_tier_all(tier, division, player_count, match_per_player)
