import os
import glob
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ===============================
# 0. 설정
# ===============================
BASE_PATH = r"C:\dev\LOL_Tier_Winrate_Analysis\data\processed"

TEMP_DIR = r"C:\dev\LOL_Tier_Winrate_Analysis\data\temp"
TEMP_DF_PATH = os.path.join(TEMP_DIR, "final_df_timebin_team100.csv")
os.makedirs(TEMP_DIR, exist_ok=True)

TIERS = [
    "IRON", "BRONZE", "SILVER", "GOLD",
    "PLATINUM", "EMERALD", "DIAMOND",
    "MASTER", "GRANDMASTER", "CHALLENGER"
]

FEATURES = [
    "goldDiff",
    "totalKillDiff",
    "dragonDiff",
    "elderDiff",
    "heraldDiff",
    "baronDiff",
    "atakhanDiff",
    "grubDiff",
    "outerTowerDiff",
    "innerTowerDiff",
    "baseTowerDiff",
]


# ===============================
# 1. timeline wide → long
# ===============================
def timeline_wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, row in df.iterrows():
        match_id = row["matchId"]

        for col in df.columns:
            if "_" not in col:
                continue

            base, minute = col.rsplit("_", 1)
            if not minute.isdigit():
                continue

            rows.append({
                "matchId": match_id,
                "time_min": int(minute),
                base: row[col]
            })

    long_df = pd.DataFrame(rows)

    long_df = (
        long_df
        .groupby(["matchId", "time_min"], as_index=False)
        .first()
    )

    return long_df


# ===============================
# 2. DF 캐시 로딩 or 생성
# ===============================
if os.path.exists(TEMP_DF_PATH):
    print(f"\n[LOAD] Cached DF: {TEMP_DF_PATH}")
    df = pd.read_csv(TEMP_DF_PATH)

else:
    print("\n[BUILD] Creating DF from raw CSVs...")
    dfs = []

    for tier in TIERS:
        timeline_files = glob.glob(f"{BASE_PATH}/*{tier}*timeline*.csv")
        match_files    = glob.glob(f"{BASE_PATH}/*{tier}*matches*.csv")

        print("\n==============================")
        print("TIER:", tier)
        print("timeline_files:", timeline_files)
        print("match_files   :", match_files)

        if not timeline_files or not match_files:
            print(">> SKIP")
            continue

        # timeline
        timeline_df = pd.concat([pd.read_csv(f) for f in timeline_files])
        long_df = timeline_wide_to_long(timeline_df)

        # match result (team100 기준)
        matches_df = pd.concat([pd.read_csv(f) for f in match_files])
        matches_df = matches_df[["matchId", "win"]].copy()
        matches_df["tier"] = tier

        merged = long_df.merge(matches_df, on="matchId", how="inner")
        dfs.append(merged)

    raw_df = pd.concat(dfs, ignore_index=True)

    # -------------------------------
    # 시간 필터 + time_bin
    # -------------------------------
    raw_df = raw_df[(raw_df["time_min"] >= 10) & (raw_df["time_min"] <= 35)]
    raw_df["time_bin"] = (raw_df["time_min"] // 5) * 5

    # -------------------------------
    # matchId + time_bin 기준 집계
    # win은 절대 평균내지 않음
    # -------------------------------
    df_feat = (
        raw_df
        .groupby(["matchId", "time_bin", "tier"], as_index=False)[FEATURES]
        .mean()
    )

    df_win = (
        raw_df
        .groupby(["matchId", "time_bin", "tier"], as_index=False)["win"]
        .first()   # team100 기준 승패
    )

    df = df_feat.merge(df_win, on=["matchId", "time_bin", "tier"])

    # -------------------------------
    # tower diff 부호 반전 (수집 오류 보정)
    # -------------------------------
    TOWER_DIFF_COLS = [
        "outerTowerDiff",
        "innerTowerDiff",
        "baseTowerDiff",
    ]

    df[TOWER_DIFF_COLS] = -df[TOWER_DIFF_COLS]

    # NaN 안전 처리
    df[FEATURES] = df[FEATURES].fillna(0)


    # 캐시 저장
    df.to_csv(TEMP_DF_PATH, index=False)
    print(f"[SAVE] Cached DF saved to: {TEMP_DF_PATH}")

print("\nFINAL DF SHAPE:", df.shape)
print(df.head())


# ===============================
# 3. 머신러닝 (team100 승률 예측)
# ===============================
X = df[FEATURES]
y = df["win"]    # team100 승리 여부 (0 / 1)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()
X_train_z = scaler.fit_transform(X_train)
X_test_z  = scaler.transform(X_test)

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(X_train_z, y_train)

y_pred = model.predict(X_test_z)

print("\n=== Accuracy ===")
print(accuracy_score(y_test, y_pred))

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))


# ===============================
# 4. Feature Importance (해설 핵심)
# ===============================
importance_df = pd.DataFrame({
    "feature": FEATURES,
    "coef": model.coef_[0]
})

importance_df["abs_coef"] = importance_df["coef"].abs()
importance_df = importance_df.sort_values("abs_coef", ascending=False)

print("\n=== Feature Importance (team100 기준) ===")
print(importance_df)


# ===============================
# 5. objective score & 예측 승률
# ===============================
test_df = df.loc[X_test.index].copy()

test_df["objective_score"] = model.decision_function(X_test_z)
test_df["predicted_winrate"] = model.predict_proba(X_test_z)[:, 1]

print("\nSample result:")
print(
    test_df[
        ["matchId", "time_bin", "tier", "objective_score", "predicted_winrate"]
    ].head()
)
