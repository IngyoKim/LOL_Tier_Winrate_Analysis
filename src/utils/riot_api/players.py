import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")
REGION_PLATFORM = "kr"

def fetch_players_by_tier(tier, division=None, page=1):
    tier = tier.upper()
    headers = {"X-Riot-Token": API_KEY}

    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        ENDPOINTS = {
            "MASTER": "masterleagues",
            "GRANDMASTER": "grandmasterleagues",
            "CHALLENGER": "challengerleagues"
        }
        url = f"https://{REGION_PLATFORM}.api.riotgames.com/lol/league/v4/{ENDPOINTS[tier]}/by-queue/RANKED_SOLO_5x5"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("하이 티어 조회 실패:", res.text)
            return []
        return res.json().get("entries", [])

    # IRON ~ DIAMOND
    if division is None:
        raise ValueError("IRON~DIAMOND 티어는 division이 필요합니다.")

    url = f"https://{REGION_PLATFORM}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
    res = requests.get(url, headers=headers, params={"page": page})

    if res.status_code != 200:
        print("티어 조회 실패:", res.text)
        return []

    return res.json()
