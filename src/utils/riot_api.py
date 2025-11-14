import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

REGION_ROUTING = "asia"   # match API
REGION_PLATFORM = "kr"    # league/summoner API


# -----------------------------
#  티어 기반 플레이어 조회
# -----------------------------
def fetch_players_by_tier(tier, division="I", page=1):
    """티어 + 디비전 + 페이지 기반 플레이어 목록 조회"""
    url = f"https://{REGION_PLATFORM}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
    params = {"page": page}
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("티어 조회 실패:", res.text)
        return []

    return res.json()


# -----------------------------
#  matchlist (puuid → matchId)
# -----------------------------
def fetch_match_ids(puuid, count=20):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("matchlist 오류:", res.text)
        return []

    return res.json()


# -----------------------------
#  match info (matchId → JSON)
# -----------------------------
def fetch_match_info(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("match info 오류:", match_id, res.text)
        return None

    return res.json()


# -----------------------------
#  match info에서 특정 플레이어 정보만 추출
# -----------------------------
def extract_player_row(match_json, puuid):
    if match_json is None:
        return None

    info = match_json["info"]
    participants = info["participants"]
    match_id = match_json["metadata"]["matchId"]

    for p in participants:
        if p["puuid"] == puuid:
            return {
                "puuid": puuid,
                "matchId": match_id,
                "champion": p["championName"],
                "win": int(p["win"]),
                "kills": p["kills"],
                "deaths": p["deaths"],
                "assists": p["assists"],
                "gold": p["goldEarned"],
                "damage": p["totalDamageDealtToChampions"],
                "lane": p["lane"],
                "role": p["role"],
                "gameDuration": info["gameDuration"]
            }

    return None
