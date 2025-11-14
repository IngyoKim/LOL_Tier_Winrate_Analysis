from src.utils.riot_api import fetch_players_by_tier
import os

def main():
    os.makedirs("data/raw", exist_ok=True)

    tier = input("티어 입력 (IRON/BRONZE/SILVER/GOLD/PLATINUM/DIAMOND): ").upper()
    division = input("디비전 입력 (I/II/III/IV): ").upper()
    target_count = int(input("가져올 플레이어 수 (예: 300): "))

    puuids = []
    page = 1

    while len(puuids) < target_count:
        players = fetch_players_by_tier(tier, division, page)

        if not players:
            print("더 이상 데이터를 가져올 수 없습니다.")
            break

        print(f"{tier} {division} page {page}: {len(players)}명 불러옴")

        for p in players:
            if "puuid" in p:
                puuids.append(p["puuid"])

        page += 1

    # 필요한 수만큼 자르기
    puuids = list(set(puuids))[:target_count]

    save_path = f"data/raw/{tier}_{division}_puuids.txt"
    with open(save_path, "w") as f:
        for puuid in puuids:
            f.write(puuid + "\n")

    print(f"총 수집된 PUUID: {len(puuids)}명 저장 완료 → {save_path}")


if __name__ == "__main__":
    main()
