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
    "P": "PLATINUM",
    "G": "GOLD",
    "S": "SILVER",
    "B": "BRONZE",
    "I": "IRON"
}

NO_DIVISION = {"C", "GM", "M"}


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


def add_total_kills(input_path: str, output_path: str):
    import pandas as pd
    import re

    df = pd.read_csv(input_path)

    # 기존 totalKill 제거
    drop_cols = [c for c in df.columns if c.startswith("totalKill")]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # 모든 kill 시간 추출
    kill_times = sorted([
        int(re.search(r"_(\d+)$", c).group(1))
        for c in df.columns if c.startswith("kill100_")
    ])

    # maxMinute 기반 종료 처리
    max_minute = df["maxMinute"]

    # totalKill 값 저장
    total_values = {}

    for t in kill_times:
        k100_list = [f"kill100_{x}" for x in kill_times if x <= t]
        k200_list = [f"kill200_{x}" for x in kill_times if x <= t]

        total100 = df[k100_list].sum(axis=1)
        total200 = df[k200_list].sum(axis=1)
        diff = total100 - total200

        # 게임 종료 minute 이후는 NA
        mask = (max_minute < t)
        total100 = total100.where(~mask, pd.NA)
        total200 = total200.where(~mask, pd.NA)
        diff = diff.where(~mask, pd.NA)

        total_values[f"totalKill100_{t}"] = total100
        total_values[f"totalKill200_{t}"] = total200
        total_values[f"totalKillDiff_{t}"] = diff

    df_total = pd.DataFrame(total_values)

    # 1) 원본 컬럼에서 t별 그룹화
    grouped = {}
    for col in df.columns:
        m = re.search(r"_(\d+)$", col)
        if m:
            t = int(m.group(1))
            grouped.setdefault(t, []).append(col)
        else:
            # 시간 없는 컬럼은 맨 앞에 유지
            grouped.setdefault("static", []).append(col)

    # 2) t별 그룹 내부에서 kill 뒤에 totalKill 삽입
    final_columns = grouped["static"][:]  # static은 그대로 앞에 둠

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

    # totalKill 값 df에 넣기
    df_final = df.copy()
    for col in df_total.columns:
        df_final[col] = df_total[col]

    df_final = df_final[final_columns]
    df_final.to_csv(output_path, index=False)

    import pandas as pd
    import re

    df = pd.read_csv(input_path)

    # 기존 totalKill 제거
    drop_cols = [c for c in df.columns if c.startswith("totalKill")]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # 모든 kill 시간 추출
    kill_times = sorted([
        int(re.search(r"_(\d+)$", c).group(1))
        for c in df.columns if c.startswith("kill100_")
    ])

    # maxMinute 기반 종료 처리
    max_minute = df["maxMinute"]

    # totalKill 값 저장
    total_values = {}

    for t in kill_times:
        k100_list = [f"kill100_{x}" for x in kill_times if x <= t]
        k200_list = [f"kill200_{x}" for x in kill_times if x <= t]

        total100 = df[k100_list].sum(axis=1)
        total200 = df[k200_list].sum(axis=1)
        diff = total100 - total200

        # 게임 종료 minute 이후는 NA
        mask = (max_minute < t)
        total100 = total100.where(~mask, pd.NA)
        total200 = total200.where(~mask, pd.NA)
        diff = diff.where(~mask, pd.NA)

        total_values[f"totalKill100_{t}"] = total100
        total_values[f"totalKill200_{t}"] = total200
        total_values[f"totalKillDiff_{t}"] = diff

    df_total = pd.DataFrame(total_values)

    # 1) 원본 컬럼에서 t별 그룹화
    grouped = {}
    for col in df.columns:
        m = re.search(r"_(\d+)$", col)
        if m:
            t = int(m.group(1))
            grouped.setdefault(t, []).append(col)
        else:
            # 시간 없는 컬럼은 맨 앞에 유지
            grouped.setdefault("static", []).append(col)

    # 2) t별 그룹 내부에서 kill 뒤에 totalKill 삽입
    final_columns = grouped["static"][:]  # static은 그대로 앞에 둠

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

    # totalKill 값 df에 넣기
    df_final = df.copy()
    for col in df_total.columns:
        df_final[col] = df_total[col]

    df_final = df_final[final_columns]
    df_final.to_csv(output_path, index=False)



if __name__ == "__main__":
    print("=== Kill Postprocess (중간 삽입 totalKill 생성기) ===")
    raw = input("티어 입력 (예: G II / I IV / C / GM / M): ").strip()

    parts = raw.split()

    if len(parts) == 1:
        tier = parts[0]
        division = None
    elif len(parts) == 2:
        tier, division = parts
    else:
        raise ValueError("형식 오류. 예: G II / I IV / C")

    filename = build_filename(tier, division)
    input_path = os.path.join(PROCESSED_DIR, filename)

    print(f"입력 파일: {input_path}")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"파일이 없습니다: {input_path}")

    add_total_kills(input_path, input_path)
    print("완료되었습니다.")
