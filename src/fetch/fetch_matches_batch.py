import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from src.utils.riot_api import fetch_match_ids, fetch_match_info, extract_player_row

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

REGION_ROUTING = "asia"

def main():
    os.makedirs("data/processed", exist_ok=True)

    puuid_file = input("PUUID 파일 경로 (예: data/raw/IRON_I_puuids.txt): ")
    match_per_player = int(input("각 플레이어 당 가져올 경기 수(예: 10): "))

    # 저장 CSV
    output_path = "data/processed/matches.csv"

    result_rows = []

    with open(puuid_file, "r") as f:
        puuid_list = [line.strip() for line in f.readlines()]

    print("총 PUUID 수:", len(puuid_list))

    for idx, puuid in enumerate(puuid_list, 1):
        print(f"[{idx}/{len(puuid_list)}] {puuid} 처리 중...")

        match_ids = fetch_match_ids(puuid, match_per_player)

        for match_id in match_ids:
            match_json = fetch_match_info(match_id)
            row = extract_player_row(match_json, puuid)

            if row:
                result_rows.append(row)

            time.sleep(1.2)  # rate limit 방지

    df = pd.DataFrame(result_rows)
    df.to_csv(output_path, index=False)

    print("저장 완료 →", output_path)


if __name__ == "__main__":
    main()
