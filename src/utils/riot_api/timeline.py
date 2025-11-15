import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")
REGION_ROUTING = "asia"


def fetch_match_timeline(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("timeline 오류:", match_id, res.text)
        return None

    return res.json()
