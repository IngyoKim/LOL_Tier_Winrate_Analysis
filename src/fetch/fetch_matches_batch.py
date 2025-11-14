import os
import time
import pandas as pd
from dotenv import load_dotenv

from src.utils.riot_api import (
    fetch_match_ids,
    fetch_match_info,
    extract_match_rows  # 팀·상대 정보 포함된 row 추출
)

load_dotenv()


def main():
    os.makedirs("data/processed", exist_ok=True)

    puuid_file = input("PUUID 파일 경로 (예: data/raw/GOLD_I_puuids.txt): ")
    match_per_player = int(input("각 플레이어 당 가져올 경기 수(예: 10): "))

    output_path = "data/processed/GOLD_I_matches.csv"

    # (핵심) 게임 중복 방지를 위한 set
    seen_matches = set()

    result_rows = []

    # PUUID 리스트 불러오기
    with open(puuid_file, "r") as f:
        puuid_list = [line.strip() for line in f.readlines()]

    print("총 PUUID 수:", len(puuid_list))

    # 각 플레이어별 경기 수집
    for idx, puuid in enumerate(puuid_list, 1):
        print(f"[{idx}/{len(puuid_list)}] {puuid} 처리 중...")

        match_ids = fetch_match_ids(puuid, match_per_player)

        for match_id in match_ids:

            # (중복 검사)
            if match_id in seen_matches:
                continue  # 이미 처리한 경기라면 스킵

            seen_matches.add(match_id)

            match_json = fetch_match_info(match_id)
            if not match_json:
                continue

            # 1경기 → 10row 
            rows = extract_match_rows(match_json)
            result_rows.extend(rows)

            time.sleep(1.2)  # rate limit 방지

    # 데이터프레임으로 변환
    df = pd.DataFrame(result_rows)
    df.to_csv(output_path, index=False)

    print("저장 완료 →", output_path)
    print("총 수집된 고유 경기 수:", len(seen_matches))
    print("총 Row 수:", len(result_rows))


if __name__ == "__main__":
    main()
