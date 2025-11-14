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
    한 경기(match_json)에서 10명 전체 스탯 + 
    팀 오브젝트 + 라인 매칭 + 오브젝트 차이

    lane = 팀별 5명 순서 강제 매핑:
    [TOP, JUNGLE, MID, ADC, SUPPORT]
    """

    if match_json is None:
        return []

    info = match_json["info"]

    # 솔랭만
    if info.get("queueId") != 420:
        return []

    metadata = match_json["metadata"]
    match_id = metadata["matchId"]
    participants = info["participants"]
    teams = info["teams"]

    # -------------------------
    # 팀 오브젝트 정보 추출
    # -------------------------
    team_obj = {}
    for t in teams:
        tid = t["teamId"]
        o = t["objectives"]
        team_obj[tid] = {
            "baron": o["baron"]["kills"],
            "dragon": o["dragon"]["kills"],
            "tower": o["tower"]["kills"],
            "herald": o["riftHerald"]["kills"],
            "inhibitor": o["inhibitor"]["kills"],
            "championKills": o["champion"]["kills"]
        }

    # -------------------------
    # lane 강제 매핑
    # -------------------------
    lane_order = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]

    # 팀 별로 참가자 분리
    team_players = {100: [], 200: []}
    for p in participants:
        team_players[p["teamId"]].append(p)

    # participantId 정렬 안 함
    # Riot은 participants 배열 자체가 participantId 순서임.
    # 그대로 인덱스로 0~4 매핑.

    # 팀별 lane 강제 적용
    for tid in [100, 200]:
        for idx, p in enumerate(team_players[tid]):
            p["_fixed_lane"] = lane_order[idx]  # 강제 라인 배정

    # -------------------------
    # 라인 매칭 (강제 lane 기반)
    # -------------------------
    lane_map = {}
    for p in participants:
        lane = p["_fixed_lane"]
        if lane not in lane_map:
            lane_map[lane] = []
        lane_map[lane].append(p)

    # -------------------------
    # 10명 row 생성
    # -------------------------
    rows = []

    for p in participants:
        team_id = p["teamId"]
        enemy_team_id = 100 if team_id == 200 else 200
        lane = p["_fixed_lane"]

        # 라인 매칭 상대 찾기
        enemy_lane_champ = None
        if lane in lane_map:
            for enemy in lane_map[lane]:
                if enemy["teamId"] != team_id:
                    enemy_lane_champ = enemy["championName"]
                    break

        # 오브젝트 차이 계산
        baronDiff = team_obj[team_id]["baron"] - team_obj[enemy_team_id]["baron"]
        dragonDiff = team_obj[team_id]["dragon"] - team_obj[enemy_team_id]["dragon"]
        towerDiff = team_obj[team_id]["tower"] - team_obj[enemy_team_id]["tower"]
        heraldDiff = team_obj[team_id]["herald"] - team_obj[enemy_team_id]["herald"]
        inhibitorDiff = team_obj[team_id]["inhibitor"] - team_obj[enemy_team_id]["inhibitor"]
        championKillDiff = team_obj[team_id]["championKills"] - team_obj[enemy_team_id]["championKills"]

        row = {
            "matchId": match_id,
            "gameDuration": info["gameDuration"],
            "playerPuuid": p["puuid"],
            "teamId": team_id,
            "win": int(p["win"]),

            # 강제 배정된 lane
            "lane": lane,

            # 개인 스탯
            "champion": p["championName"],
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "gold": p["goldEarned"],
            "damage": p["totalDamageDealtToChampions"],

            # 아군 오브젝트
            "allyBaron": team_obj[team_id]["baron"],
            "allyDragon": team_obj[team_id]["dragon"],
            "allyTower": team_obj[team_id]["tower"],
            "allyHerald": team_obj[team_id]["herald"],
            "allyInhibitor": team_obj[team_id]["inhibitor"],
            "allyChampionKills": team_obj[team_id]["championKills"],

            # 적군 오브젝트
            "enemyBaron": team_obj[enemy_team_id]["baron"],
            "enemyDragon": team_obj[enemy_team_id]["dragon"],
            "enemyTower": team_obj[enemy_team_id]["tower"],
            "enemyHerald": team_obj[enemy_team_id]["herald"],
            "enemyInhibitor": team_obj[enemy_team_id]["inhibitor"],
            "enemyChampionKills": team_obj[enemy_team_id]["championKills"],

            # 오브젝트 차이
            "baronDiff": baronDiff,
            "dragonDiff": dragonDiff,
            "towerDiff": towerDiff,
            "heraldDiff": heraldDiff,
            "inhibitorDiff": inhibitorDiff,
            "championKillDiff": championKillDiff,

            # 라인 상대 챔피언
            "enemyLaneChampion": enemy_lane_champ
        }

        rows.append(row)

    return rows
