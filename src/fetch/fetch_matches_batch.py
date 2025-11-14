from src.utils.riot_api import fetch_match_ids, fetch_match_info, extract_match_rows
import os
import time
import pandas as pd

def main():
    os.makedirs("data/processed", exist_ok=True)

    puuid_file = input("PUUID 파일 경로: ")
    match_per_player = int(input("각 플레이어 당 가져올 경기 수: "))

    output_path = "data/processed/matches_full.csv"
    result_rows = []

    with open(puuid_file, "r") as f:
        puuid_list = [line.strip() for line in f.readlines()]

    print("총 PUUID:", len(puuid_list))

    for idx, puuid in enumerate(puuid_list, 1):
        print(f"[{idx}/{len(puuid_list)}] {puuid} 처리 중...")

        match_ids = fetch_match_ids(puuid, match_per_player)

        for match_id in match_ids:
            match_json = fetch_match_info(match_id)
            rows = extract_match_rows(match_json)
            result_rows.extend(rows)

            time.sleep(1.2)

    df = pd.DataFrame(result_rows)
    df.to_csv(output_path, index=False)

    print("완료:", output_path)

if __name__ == "__main__":
    main()
