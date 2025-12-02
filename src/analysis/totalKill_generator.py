#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

PROCESSED_DIR = "data/processed"

TIER_MAP = {
    "C": "CHALLENGER",
    "GM": "GRANDMASTER",
    "M": "MASTER",
    "D": "DIAMOND",
    "E": "EMERALD",
    "P": "PLATINUM",
    "G": "GOLD",
    "S": "SILVER",
    "B": "BRONZE",
    "I": "IRON"
}

NO_DIVISION = {"C", "GM", "M"}   # 세부티어 없음
DIVISIONS = ["I", "II", "III", "IV"]


def build_filename(tier: str, division: str | None):
    tier = tier.upper()
    if tier not in TIER_MAP:
        raise ValueError(f"존재하지 않는 티어 입력: {tier}")

    tier_name = TIER_MAP[tier]

    # C / GM / M 은 세부티어 없음
    if tier in NO_DIVISION:
        return f"{tier_name}_timeline.csv"

    if not division:
        raise ValueError(f"{tier_name} 티어는 세부티어(I~IV)를 입력해야 합니다.")

    division = division.upper()
    return f"{tier_name}_{division}_timeline.csv"


########################################
#       ★ totalKill 생성 함수 그대로 ★
########################################
def add_total_kills(input_path: str, output_path: str):
    import pandas as pd
    import re

    df = pd.read_csv(input_path)

    drop_cols = [c for c in df.columns if c.startswith("totalKill")]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    kill_times = sorted([
        int(re.search(r"_(\d+)$", c).group(1))
        for c in df.columns if c.startswith("kill100_")
    ])

    max_minute = df["maxMinute"]

    total_values = {}
    for t in kill_times:
        k100_list = [f"kill100_{x}" for x in kill_times if x <= t]
        k200_list = [f"kill200_{x}" for x in kill_times if x <= t]

        total100 = df[k100_list].sum(axis=1)
        total200 = df[k200_list].sum(axis=1)
        diff = total100 - total200

        mask = (max_minute < t)
        total100 = total100.where(~mask, pd.NA)
        total200 = total200.where(~mask, pd.NA)
        diff = diff.where(~mask, pd.NA)

        total_values[f"totalKill100_{t}"] = total100
        total_values[f"totalKill200_{t}"] = total200
        total_values[f"totalKillDiff_{t}"] = diff

    df_total = pd.DataFrame(total_values)

    # 그룹화
    import re
    grouped = {}
    for col in df.columns:
        m = re.search(r"_(\d+)$", col)
        if m:
            t = int(m.group(1))
            grouped.setdefault(t, []).append(col)
        else:
            grouped.setdefault("static", []).append(col)

    final_columns = grouped["static"][:]

    for t in kill_times:
        block = grouped[t][:]
        new_block = []
        for col in block:
            new_block.append(col)

            if col == f"kill100_{t}":
                new_block.append(f"totalKill100_{t}")
            if col == f"kill200_{t}":
                new_block.append(f"totalKill200_{t}")
            if col == f"killDiff_{t}":
                new_block.append(f"totalKillDiff_{t}")

        final_columns.extend(new_block)

    df_final = df.copy()
    for col in df_total.columns:
        df_final[col] = df_total[col]

    df_final = df_final[final_columns]
    df_final.to_csv(output_path, index=False)


########################################
#       ★ 메인 로직 확장 구현 ★
########################################
def get_target_files(user_input: str):
    """
    사용자 입력을 해석해 여러 파일 경로 리스트로 반환.
    """
    user_input = user_input.strip()

    # 1) 아무것도 입력 안 한 경우 → 전체 티어 처리
    if user_input == "":
        all_files = []

        # division 없는 티어 3개
        for tier in NO_DIVISION:
            name = build_filename(tier, None)
            all_files.append(name)

        # division 있는 티어들
        for tier in TIER_MAP:
            if tier in NO_DIVISION:
                continue
            for div in DIVISIONS:
                name = build_filename(tier, div)
                all_files.append(name)

        return all_files

    # 2) "G"처럼 티어만 입력 → 세부티어 전체 처리
    parts = user_input.split()

    if len(parts) == 1:
        tier = parts[0].upper()

        if tier in NO_DIVISION:
            return [build_filename(tier, None)]

        if tier in TIER_MAP:
            return [build_filename(tier, div) for div in DIVISIONS]

        raise ValueError("존재하지 않는 티어입니다.")

    # 3) "G II" 처럼 tier + division
    if len(parts) == 2:
        tier, division = parts
        return [build_filename(tier, division)]

    raise ValueError("입력 형식 오류. 예: G / G II / C / (공백) 전체 처리")


########################################
#                MAIN
########################################
if __name__ == "__main__":
    print("========= Kill Postprocess (중간 삽입 totalKill 생성기) =========")
    print("----------------------------입력 방법----------------------------")
    print("세부 티어별 G I(Gold I) / 전체 티어별 G(Gold I~IV) / 전체 공백 입력")
    raw = input("티어 입력: ").strip()

    targets = get_target_files(raw)

    print("\n처리할 파일 목록:")
    for f in targets:
        print(" -", f)

    for filename in targets:
        input_path = os.path.join(PROCESSED_DIR, filename)

        if not os.path.exists(input_path):
            print(f"[경고] 파일 없음: {input_path}")
            continue

        print(f"[처리중] {filename}")
        add_total_kills(input_path, input_path)

    print("\n=== 완료되었습니다 ===")
