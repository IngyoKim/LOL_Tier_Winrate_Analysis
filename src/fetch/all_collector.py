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

# ---------------------------------------------------------
# 티어 설정
# ---------------------------------------------------------
NORMAL_TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
DIVISIONS = ["I", "II", "III", "IV"]
HIGH_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]

# =========================
# 글로벌 안정 설정
# =========================
BATCH_SIZE = 3
BATCH_SLEEP = 3.0
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
# match info + timeline 안정 요청
# -----------------------------------------------------------
async def fetch_full_match(session, match_id):

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
    print("===================================================\n")

    os.makedirs("data/processed", exist_ok=True)

    finish_rows = []
    timeline_rows = []

    all_match_ids = []

    print("▶ matchlist 수집 중...")

    for puuid in puuids:
        match_ids = await fetch_match_ids(session, puuid, match_per_player)
        all_match_ids.extend(match_ids)

        await asyncio.sleep(1.0)

    all_match_ids = list(set(all_match_ids))

    print(f"✔ 총 고유 matchId: {len(all_match_ids)}개 수집 완료\n")

    # ---------------------------
    # batch로 match 처리
    # ---------------------------
    print("▶ match info + timeline 수집 중...")

    for i in range(0, len(all_match_ids), BATCH_SIZE):
        batch = all_match_ids[i:i + BATCH_SIZE]
        print(f"  → batch {i//BATCH_SIZE + 1} 처리 중 ({len(batch)}개)")

        tasks = [fetch_full_match(session, m) for m in batch]
        results = await asyncio.gather(*tasks)

        for (match_json, timeline_json), match_id in zip(results, batch):

            if not match_json or not timeline_json:
                print(f"    · {match_id} → (오류 → 건너뜀)")
                continue

            finish = extract_match_rows(match_json)
            finish_rows.extend(finish)

            timeline = extract_timeline_features(match_json, timeline_json)
            if timeline:
                timeline_rows.append(timeline)

        await asyncio.sleep(BATCH_SLEEP)

    # ---------------------------
    # CSV 저장
    # ---------------------------
    finish_path = f"data/processed/{tier_name}_matches.csv"
    timeline_path = f"data/processed/{tier_name}_timeline.csv"

    pd.DataFrame(finish_rows).to_csv(finish_path, index=False)
    pd.DataFrame(timeline_rows).to_csv(timeline_path, index=False)

    print("\n===================================================")
    print(f"✔ FINISH row 수: {len(finish_rows)}개 → {finish_path}")
    print(f"✔ TIMELINE row 수: {len(timeline_rows)}개 → {timeline_path}")
    print("===================================================\n")

    return finish_path, timeline_path


# -----------------------------------------------------------
# 3) 티어 하나 수집
# -----------------------------------------------------------
async def collect_tier_all(tier, division=None, player_count=300, match_per_player=10):

    print("=============================================")
    print(f"▶ 티어 수집 시작: {tier} {division or ''}")
    print("=============================================\n")

    tier = tier.upper()
    if division:
        division = division.upper()

    async with aiohttp.ClientSession() as session:

        puuids, tier_name = await collect_puuids(session, tier, division, player_count)

        finish_path, timeline_path = await collect_matches_from_puuids(
            session, puuids, tier_name, match_per_player
        )

    return finish_path, timeline_path


# -----------------------------------------------------------
# 4) 전체 티어 자동 수집
# -----------------------------------------------------------
async def collect_all_tiers(player_count=300, match_per_player=10, delay=3.0, use_division=True):

    print("=====================================================")
    print("▶ All Tier Collector 시작")
    print("=====================================================\n")

    # 1) IRON ~ DIAMOND
    for tier in NORMAL_TIERS:

        print(f"\n---------------------------------------------------")
        print(f"▶ 수집 시작: {tier}")
        print("---------------------------------------------------")

        if use_division:
            # 기존 방식: I~IV 각각 처리
            for div in DIVISIONS:
                tier_name = f"{tier} {div}"
                print(f"  → {tier_name} 진행")

                try:
                    await collect_tier_all(
                        tier=tier,
                        division=div,
                        player_count=player_count,
                        match_per_player=match_per_player
                    )
                except Exception as e:
                    print(f"❌ 오류 발생 (건너뜀): {tier_name}")
                    print("   오류:", e)

                await asyncio.sleep(delay)

        else:
            # 새 방식: division 안 씀 → player_count를 4등분해서 배분
            per_div = player_count // 4
            remainder = player_count % 4

            for i, div in enumerate(DIVISIONS):
                alloc = per_div + (1 if i < remainder else 0)

                print(f"  → {tier} division {div}에서 {alloc}명 수집")

                try:
                    await collect_tier_all(
                        tier=tier,
                        division=div,
                        player_count=alloc,
                        match_per_player=match_per_player
                    )
                except Exception as e:
                    print(f"❌ 오류 발생 (건너뜀): {tier} {div}")
                    print("   오류:", e)

                await asyncio.sleep(delay)

        print(f"✔ 완료: {tier}")

    # 2) MASTER ~ CHALLENGER는 division 없음
    for tier in HIGH_TIERS:

        print(f"\n---------------------------------------------------")
        print(f"▶ 수집 시작: {tier}")
        print("---------------------------------------------------")

        try:
            await collect_tier_all(
                tier=tier,
                division=None,
                player_count=player_count,
                match_per_player=match_per_player
            )
        except Exception as e:
            print(f"❌ 오류 발생 (건너뜀): {tier}")
            print("   오류:", e)

        print(f"✔ 완료: {tier}")
        await asyncio.sleep(delay)

    print("=====================================================")
    print("🎉 All Tier Collector 전체 완료")
    print("=====================================================")

# -----------------------------------------------------------
# CLI
# -----------------------------------------------------------
if __name__ == "__main__":
    print("==============================================")
    print("LOL 전체 티어 자동 Collector")
    print("==============================================")

    player_count = int(input("티어당 수집할 플레이어 수 (예: 300): ").strip())
    match_per_player = int(input("플레이어당 match 수 (예: 10): ").strip())
    use_division = input("세부 티어 구분 사용 여부(y/n): ").strip().lower() == "y"
    
    delay = 3.0

    asyncio.run(
        collect_all_tiers(
            player_count=player_count,
            match_per_player=match_per_player,
            delay=delay,
            use_division=use_division
        )
    )
