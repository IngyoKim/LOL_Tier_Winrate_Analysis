import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

REGION_ROUTING = "asia"
REGION_PLATFORM = "kr"

def fetch_match_ids(puuid, count=20):
    """puuid 기반으로 최근 경기 matchId 리스트 가져오기"""
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("matchlist 불러오기 실패:", res.text)
        return []

    return res.json()


def fetch_match_info(match_id):
    """matchId 기반으로 match 정보 가져오기"""
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("match info 불러오기 실패:", match_id, res.text)
        return None

    return res.json()


def extract_player_data(match_json, puuid):
    """match JSON에서 해당 플레이어의 전적 정보 추출"""
    if match_json is None:
        return None

    info = match_json["info"]
    participants = info["participants"]

    for p in participants:
        if p["puuid"] == puuid:
            return {
                "puuid": puuid,
                "matchId": match_json["metadata"]["matchId"],
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


def main():
    os.makedirs("data/processed", exist_ok=True)
    
    puuid = input("PUUID 입력: ")
    match_count = int(input("가져올 경기 수(예: 20): "))

    match_ids = fetch_match_ids(puuid, match_count)
    print("가져온 matchId:", len(match_ids))

    data_list = []

    for match_id in match_ids:
        match_json = fetch_match_info(match_id)
        time.sleep(1.2)   # rate limit 방지
        row = extract_player_data(match_json, puuid)
        if row:
            data_list.append(row)

    df = pd.DataFrame(data_list)
    df.to_csv("data/processed/sample_matches.csv", index=False)

    print("저장 완료: data/processed/sample_matches.csv")


if __name__ == "__main__":
    main()
