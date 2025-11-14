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
    """match info에서 해당 플레이어 정보 + 팀 오브젝트까지 모두 추출"""

    if match_json is None:
        return None

    info = match_json["info"]
    participants = info["participants"]
    match_id = match_json["metadata"]["matchId"]

    # -----------------------
    # 플레이어 정보 찾기
    # -----------------------
    player_data = None
    for p in participants:
        if p["puuid"] == puuid:
            player_data = p
            break

    if player_data is None:
        return None

    team_id = player_data["teamId"]   # 100 또는 200

    # -----------------------
    # 팀 오브젝트 정보 찾기
    # -----------------------
    team_obj = None
    for team in info["teams"]:
        if team["teamId"] == team_id:
            team_obj = team["objectives"]
            break

    if team_obj is None:
        return None

    # -----------------------
    # 데이터 구성
    # -----------------------
    return {
        # 기본 정보
        "puuid": puuid,
        "matchId": match_id,
        "champion": player_data["championName"],
        "win": int(player_data["win"]),

        # 개인 스탯
        "kills": player_data["kills"],
        "deaths": player_data["deaths"],
        "assists": player_data["assists"],
        "gold": player_data["goldEarned"],
        "damage": player_data["totalDamageDealtToChampions"],
        "lane": player_data["lane"],
        "role": player_data["role"],
        "gameDuration": info["gameDuration"],

        # 팀 오브젝트 정리
        "teamBaron": team_obj["baron"]["kills"],
        "teamDragon": team_obj["dragon"]["kills"],
        "teamTower": team_obj["tower"]["kills"],
        "teamHerald": team_obj["riftHerald"]["kills"],
        "teamInhibitor": team_obj["inhibitor"]["kills"],
        "teamChampionKills": team_obj["champion"]["kills"]
    }
