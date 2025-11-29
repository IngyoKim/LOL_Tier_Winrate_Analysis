import os
import asyncio
import random
import pandas as pd
import aiohttp

from src.utils.riot_api import (
    fetch_players_by_tier,
    fetch_match_ids,
    fetch_match_info,
    fetch_match_timeline,
    extract_match_rows,
    extract_timeline_features
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

# =========================
# 글로벌 설정 (안정화 핵심)
# =========================
BATCH_SIZE = 3         # 5 → 3 로 낮춰 안정화
BATCH_SLEEP = 3.0      # 배치 간 대기
REQUEST_PAUSE_MIN = 0.3
REQUEST_PAUSE_MAX = 0.7


# -----------------------------------------------------------
# 1) PUUID 수집
# -----------------------------------------------------------
async def collect_puuids(session, tier: str, division: str | None, target_count: int):
    print("===================================================")
    print(f"▶ PUUID 수집 시작: {tier} {division or ''} / 목표 {target_count}명")
    print("===================================================\n")

    os.makedirs("data/raw", exist_ok=True)

    puuids = []
    page = 1

    while len(puuids) < target_count:
        print(f"  - 페이지 요청: page {page}")

        players = await fetch_players_by_tier(session, tier, division, page)

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
        await asyncio.sleep(1.0)

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
# match info + timeline 안정 요청 함수
# -----------------------------------------------------------
async def fetch_full_match(session, match_id):

    # 요청 간 랜덤 딜레이
    await asyncio.sleep(random.uniform(REQUEST_PAUSE_MIN, REQUEST_PAUSE_MAX))

    info = await fetch_match_info(session, match_id)

    await asyncio.sleep(random.uniform(REQUEST_PAUSE_MIN, REQUEST_PAUSE_MAX))

    timeline = await fetch_match_timeline(session, match_id)

    return info, timeline



# -----------------------------------------------------------
# 2) Match 정보 수집 (finish + timeline)
# -----------------------------------------------------------
async def collect_matches_from_puuids(session, puuids, tier_name, match_per_player):
    print("===================================================")
    print(f"▶ Match 정보 수집 시작: {tier_name}")
    print(f"▶ 대상 PUUID 수: {len(puuids)}명")
    print("===================================================\n")

    os.makedirs("data/processed", exist_ok=True)

    finish_rows = []
    timeline_rows = []
    seen = set()

    # ---------------------------
    # 1) 모든 match id 먼저 수집
    # ---------------------------
    all_match_ids = []

    print("▶ matchlist 수집 중...")

    for idx, puuid in enumerate(puuids, 1):
        match_ids = await fetch_match_ids(session, puuid, match_per_player)
        all_match_ids.extend(match_ids)

        await asyncio.sleep(1.0)

    all_match_ids = list(set(all_match_ids))

    print(f"✔ 총 고유 matchId: {len(all_match_ids)}개 수집 완료\n")

    # ---------------------------
    # 2) batch로 match 처리
    # ---------------------------
    print("▶ match info + timeline 수집 중...")

    for i in range(0, len(all_match_ids), BATCH_SIZE):
        batch = all_match_ids[i:i + BATCH_SIZE]
        print(f"\n  → batch {i//BATCH_SIZE + 1} 처리 중 ({len(batch)}개)")

        tasks = [fetch_full_match(session, m) for m in batch]
        results = await asyncio.gather(*tasks)

        for (match_json, timeline_json), match_id in zip(results, batch):

            if not match_json or not timeline_json:
                print(f"    · {match_id} → (오류 → 건너뜀)")
                continue

            # FINISH extract
            finish = extract_match_rows(match_json)
            finish_rows.extend(finish)

            # TIMELINE extract
            timeline = extract_timeline_features(match_json, timeline_json)
            if timeline:
                timeline_rows.append(timeline)

        # 배치 간 대기
        await asyncio.sleep(BATCH_SLEEP)

    # ---------------------------
    # CSV 저장
    # ---------------------------
    finish_path = f"data/processed/{tier_name}_matches.csv"
    timeline_path = f"data/processed/{tier_name}_timeline.csv"

    pd.DataFrame(finish_rows).to_csv(finish_path, index=False)
    pd.DataFrame(timeline_rows).to_csv(timeline_path, index=False)

    print("\n===================================================")
    print("✔ Match 정보 수집 완료")
    print(f"✔ FINISH row 수: {len(finish_rows)}개 → {finish_path}")
    print(f"✔ TIMELINE row 수: {len(timeline_rows)}개 → {timeline_path}")
    print("===================================================\n")

    return finish_path, timeline_path


# -----------------------------------------------------------
# 3) 전체 orchestrator
# -----------------------------------------------------------
async def collect_tier_all(tier, division=None, player_count=300, match_per_player=10):
    print("=============================================")
    print("▶ 티어 전체 병렬 수집 시작")
    print("=============================================\n")

    tier = tier.upper()
    if division:
        division = division.upper()

    async with aiohttp.ClientSession() as session:

        puuids, tier_name = await collect_puuids(session, tier, division, player_count)

        finish_path, timeline_path = await collect_matches_from_puuids(
            session, puuids, tier_name, match_per_player
        )

    print("=============================================")
    print("🎉 전체 작업 완료")
    print(f"➡ FINISH CSV: {finish_path}")
    print(f"➡ TIMELINE CSV: {timeline_path}")
    print("=============================================")

    return finish_path, timeline_path


# -----------------------------------------------------------
# CLI
# -----------------------------------------------------------
if __name__ == "__main__":
    raw_tier = input("Tier 입력(C/GM/M/D/E/P/G/S/B/I): ").upper().strip()
    division = input("Division 입력(I/II/III/IV 또는 빈칸): ").upper().strip() or None
    player_count = int(input("플레이어 수: "))
    match_per_player = int(input("플레이어당 경기 수: "))

    if raw_tier not in TIER_MAP:
        print("잘못된 티어 입력입니다.")
        exit()

    tier = TIER_MAP[raw_tier]

    asyncio.run(
        collect_tier_all(tier, division, player_count, match_per_player)
    )
