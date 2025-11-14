from src.utils.riot_api import fetch_players_by_tier
import os

def main():
    os.makedirs("data/raw", exist_ok=True)

    tier = input("티어 입력 (IRON/BRONZE/SILVER/GOLD/PLATINUM/DIAMOND/MASTER/GRANDMASTER/CHALLENGER): ").upper()

    # MASTER+ 구간은 division 없음
    HIGH_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]

    if tier in HIGH_TIERS:
        division = None
        print(f"{tier} 티어는 division 입력이 필요 없습니다.")
    else:
        division = input("디비전 입력 (I/II/III/IV): ").upper()

    target_count = int(input("가져올 플레이어 수 (예: 300): "))

    puuids = []
    page = 1

    while len(puuids) < target_count:
        players = fetch_players_by_tier(tier, division, page)

        if not players:
            print("더 이상 데이터를 가져올 수 없습니다.")
            break

        # division 없는 tier는 page 정보 출력 생략
        if division:
            print(f"{tier} {division} page {page}: {len(players)}명 불러옴")
        else:
            print(f"{tier} 전체 조회: {len(players)}명 불러옴")

        for p in players:
            if "puuid" in p:
                puuids.append(p["puuid"])

        # MASTER~CHALLENGER는 page 없이 전체가 한 번에 반환됨 → 더 나눌 필요 없음
        if tier in HIGH_TIERS:
            break

        page += 1

    # 중복 제거 + 필요한 수만큼 자르기
    puuids = list(set(puuids))[:target_count]

    # 파일 이름 구분 방식
    if division:
        save_path = f"data/raw/{tier}_{division}_puuids.txt"
    else:
        save_path = f"data/raw/{tier}_puuids.txt"

    with open(save_path, "w") as f:
        for puuid in puuids:
            f.write(puuid + "\n")

    print(f"총 수집된 PUUID: {len(puuids)}명 저장 완료 → {save_path}")


if __name__ == "__main__":
    main()
