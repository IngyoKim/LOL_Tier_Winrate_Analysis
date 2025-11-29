import time
from src.fetch.collector import collect_tier_all

# 티어 구성
NORMAL_TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
DIVISIONS = ["I", "II", "III", "IV"]

HIGH_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]


def collect_all_tiers(player_count=300, match_per_player=10, delay=3.0):
    """
    모든 티어를 순회하며 데이터 자동 수집.
    잘 때 돌리라고 만든 전체 자동 collector.
    """

    print("=====================================================")
    print("▶ All Tier Collector 시작")
    print("  - Player Count :", player_count)
    print("  - Match Per Player:", match_per_player)
    print("  - Delay:", delay, "초")
    print("=====================================================\n")

    # -----------------------------
    # 1) IRON~DIAMOND (division 필요)
    # -----------------------------
    for tier in NORMAL_TIERS:
        for div in DIVISIONS:
            tier_name = f"{tier} {div}"

            print("\n-----------------------------------------------------")
            print(f"▶ 수집 시작: {tier_name}")
            print("-----------------------------------------------------")

            try:
                collect_tier_all(
                    tier=tier,
                    division=div,
                    player_count=player_count,
                    match_per_player=match_per_player
                )
            except Exception as e:
                print(f"❌ 오류 발생 (건너뜀): {tier_name}")
                print("   오류 내용:", e)

            print(f"✔ 완료: {tier_name}\n")
            time.sleep(delay)

    # -----------------------------
    # 2) MASTER~CHALLENGER (division 없음)
    # -----------------------------
    for tier in HIGH_TIERS:

        print("\n-----------------------------------------------------")
        print(f"▶ 수집 시작: {tier}")
        print("-----------------------------------------------------")

        try:
            collect_tier_all(
                tier=tier,
                division=None,
                player_count=player_count,
                match_per_player=match_per_player
            )
        except Exception as e:
            print(f"❌ 오류 발생 (건너뜀): {tier}")
            print("   오류 내용:", e)

        print(f"✔ 완료: {tier}\n")
        time.sleep(delay)

    print("=====================================================")
    print("🎉 All Tier Collector 전체 완료")
    print("=====================================================")


# ---------------------------------------------------------
# main: 사용자 입력받기
# ---------------------------------------------------------
if __name__ == "__main__":
    print("==============================================")
    print("LOL 전체 티어 자동 Collector")
    print("==============================================")

    # 사용자 입력
    player_count = int(input("티어당 수집할 플레이어 수 입력 (예: 300): ").strip())
    match_per_player = int(input("1인당 가져올 match 수 입력 (예: 10): ").strip())

    # 너무 공격적으로 돌리면 rate limit 위험
    delay = float(input("티어 간 대기 시간(sec, 기본 3.0): ").strip() or 3.0)

    print("\n입력 확인:")
    print(f"  - Player Count: {player_count}")
    print(f"  - Match per Player: {match_per_player}")
    print(f"  - Delay: {delay}초")
    print("==============================================\n")

    collect_all_tiers(
        player_count=player_count,
        match_per_player=match_per_player,
        delay=delay
    )
