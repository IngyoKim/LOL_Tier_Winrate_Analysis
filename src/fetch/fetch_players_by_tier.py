import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")
REGION = "kr"

def fetch_summoners_by_tier(tier, division="I", page=1):
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
    params = {"page": page}
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("티어 조회 실패:", res.text)
        return []

    return res.json()


def main():
    tier = input("티어 입력 (IRON/BRONZE/SILVER/GOLD/PLATINUM/DIAMOND): ").upper()
    division = input("디비전 입력 (I, II, III, IV): ").upper()
    page = int(input("페이지 번호 입력(1~5): "))

    players = fetch_summoners_by_tier(tier, division, page)

    print(f"{tier} {division} 페이지 {page} 소환사 수: {len(players)}명")

    print("=== PUUID 추출 결과 ===")
    for p in players[:10]:
        print("puuid:", p["puuid"])


if __name__ == "__main__":
    main()