import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

REGION_ROUTING = "asia"   # match API
REGION_PLATFORM = "kr"    # league/summoner API


# --------------------------------------------------------
#  티어 기반 플레이어 조회
# --------------------------------------------------------
def fetch_players_by_tier(tier, division=None, page=1):
    """
    티어에 따라 적절한 API 호출:
    - IRON~DIAMOND: entries API + division + page
    - MASTER/GRANDMASTER/CHALLENGER: 단일 API
    """
    tier = tier.upper()
    headers = {"X-Riot-Token": API_KEY}

    # MASTER / GM / CHALLENGER 구간
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

        data = res.json()
        return data.get("entries", [])

    # IRON ~ DIAMOND 구간
    if division is None:
        raise ValueError("IRON~DIAMOND 티어는 division(I/II/III/IV)이 필요합니다.")

    url = f"https://{REGION_PLATFORM}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
    params = {"page": page}

    res = requests.get(url, headers=headers, params=params)

    if res.status_code != 200:
        print("티어 조회 실패:", res.text)
        return []

    return res.json()


# --------------------------------------------------------
#  matchlist (puuid → matchId)
# --------------------------------------------------------
def fetch_match_ids(puuid, count=20):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("matchlist 오류:", res.text)
        return []

    return res.json()


# --------------------------------------------------------
#  match info (matchId → JSON)
# --------------------------------------------------------
def fetch_match_info(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("match info 오류:", match_id, res.text)
        return None

    return res.json()


# --------------------------------------------------------
#  match info → CSV row (10명)
# --------------------------------------------------------
def extract_match_rows(match_json):
    """
    한 경기에서 10명의 participant-level 최소 정보만 생성.

    남는 컬럼:
    - matchId
    - gameDuration
    - playerPuuid
    - teamId
    - win
    - lane (강제 매핑)
    - champion
    - enemyLaneChampion
    """

    if match_json is None:
        return []

    info = match_json["info"]

    # 솔랭만 사용
    if info.get("queueId") != 420:
        return []

    metadata = match_json["metadata"]
    match_id = metadata["matchId"]
    game_duration = info["gameDuration"]
    participants = info["participants"]

    # -------------------------
    # 강제 라인 매핑 그대로 유지
    # -------------------------
    lane_order = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]

    # 팀별 분류
    team_players = {100: [], 200: []}
    for p in participants:
        team_players[p["teamId"]].append(p)

    # 강제 라인 배정
    for tid in [100, 200]:
        for idx, p in enumerate(team_players[tid]):
            p["_fixed_lane"] = lane_order[idx]

    # -------------------------
    # lane 기반 상대 매칭
    # -------------------------
    lane_map = {}
    for p in participants:
        lane = p["_fixed_lane"]
        lane_map.setdefault(lane, [])
        lane_map[lane].append(p)

    # -------------------------
    # 최종 row 생성
    # -------------------------
    rows = []

    for p in participants:
        team_id = p["teamId"]
        lane = p["_fixed_lane"]

        # 라인 상대 찾기
        enemy_lane_champ = None
        for enemy in lane_map.get(lane, []):
            if enemy["teamId"] != team_id:
                enemy_lane_champ = enemy["championName"]
                break

        row = {
            "matchId": match_id,
            "gameDuration": game_duration,
            "playerPuuid": p["puuid"],
            "teamId": team_id,
            "win": int(p["win"]),
            "lane": lane,
            "champion": p["championName"],
            "enemyLaneChampion": enemy_lane_champ,
        }

        rows.append(row)

    return rows
