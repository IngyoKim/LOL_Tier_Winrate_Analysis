import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

REGION_ROUTING = "asia"
REGION_PLATFORM = "kr"


def fetch_match_ids(puuid, count=20):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    headers = {"X-Riot-Token": API_KEY}
    res = requests.get(url, headers=headers, params={"start": 0, "count": count})

    if res.status_code != 200:
        print("matchlist 오류:", res.text)
        return []

    return res.json()


def fetch_match_info(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("match info 오류:", res.text)
        return None

    return res.json()
