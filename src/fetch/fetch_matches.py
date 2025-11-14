import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv
from src.utils.riot_api import fetch_match_ids, fetch_match_info, extract_player_row

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

REGION_ROUTING = "asia"
REGION_PLATFORM = "kr"

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
        row = extract_player_row(match_json, puuid)
        if row:
            data_list.append(row)

    df = pd.DataFrame(data_list)
    df.to_csv("data/processed/sample_matches.csv", index=False)

    print("저장 완료: data/processed/sample_matches.csv")


if __name__ == "__main__":
    main()
