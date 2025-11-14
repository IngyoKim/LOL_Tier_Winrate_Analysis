import os
import time
import pandas as pd
from dotenv import load_dotenv

from src.utils.riot_api import (
    fetch_match_ids,
    fetch_match_info,
    extract_match_rows
)

load_dotenv()


def main():
    os.makedirs("data/processed", exist_ok=True)

    puuid_file = input("PUUID 파일 경로 (예: data/raw/GOLD_I_puuids.txt): ").strip()
    match_per_player = int(input("각 플레이어 당 가져올 경기 수(예: 10): "))

    # -------------------------
    # 입력한 파일명에서 티어 추출
    # -------------------------
    puuid_filename = os.path.basename(puuid_file)          # GOLD_I_puuids.txt
    tier_name = puuid_filename.replace("_puuids.txt", "")  # GOLD_I

    # 자동 출력 경로 생성
    output_path = f"data/processed/{tier_name}_matches.csv"

    # -------------------------
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
        time.sleep(1.2)

        for match_id in match_ids:

            if match_id in seen_matches:
                continue

            seen_matches.add(match_id)

            match_json = fetch_match_info(match_id)
            if not match_json:
                continue

            rows = extract_match_rows(match_json)
            result_rows.extend(rows)

            time.sleep(1.2)

    df = pd.DataFrame(result_rows)
    df.to_csv(output_path, index=False)

    print("저장 완료 →", output_path)
    print("총 수집된 고유 경기 수:", len(seen_matches))
    print("총 Row 수:", len(result_rows))


if __name__ == "__main__":
    main()
