import pandas as pd

def analyze_champion_winrate(df):
    """챔피언별 승률 및 기본 스탯 분석"""
    champ_stats = (
        df.groupby("champion")
        .agg(
            games=("win", "count"),
            wins=("win", "sum"),
            avg_kills=("kills", "mean"),
            avg_deaths=("deaths", "mean"),
            avg_assists=("assists", "mean"),
            avg_gold=("gold", "mean"),
            avg_damage=("damage", "mean")
        )
    )
    champ_stats["winrate"] = champ_stats["wins"] / champ_stats["games"] * 100
    return champ_stats.sort_values("games", ascending=False)


def analyze_lane_performance(df):
    """라인별 승률 및 KDA 분석"""

    # death가 0인 경우 division by zero 방지
    df["kda"] = (df["kills"] + df["assists"]) / df["deaths"].replace(0, 1)

    lane_stats = (
        df.groupby("lane")
        .agg(
            games=("win", "count"),
            wins=("win", "sum"),
            winrate=("win", "mean"),
            avg_kda=("kda", "mean"),
            avg_kills=("kills", "mean"),
            avg_deaths=("deaths", "mean"),
            avg_assists=("assists", "mean"),
        )
    )

    lane_stats["winrate"] = lane_stats["winrate"] * 100
    return lane_stats.sort_values("games", ascending=False)


def analyze_role(df):
    """ROLE 기준 분석"""
    role_stats = (
        df.groupby("role")
        .agg(
            games=("win", "count"),
            wins=("win", "sum"),
            winrate=("win", "mean"),
            avg_kills=("kills", "mean"),
            avg_deaths=("deaths", "mean"),
            avg_assists=("assists", "mean"),
        )
    )
    role_stats["winrate"] = role_stats["winrate"] * 100
    return role_stats.sort_values("games", ascending=False)


def main():
    print("분석할 CSV 파일 경로를 입력하세요:", end=" ")
    path = input().strip()

    df = pd.read_csv(path)
    print(f"총 데이터 개수: {len(df)}\n")

    # 챔피언 승률 분석
    print("=== 챔피언 승률 ===")
    champ_stats = analyze_champion_winrate(df)
    print(champ_stats)
    print()

    # 라인별 성능 분석
    print("=== 라인별 성능 ===")
    lane_stats = analyze_lane_performance(df)
    print(lane_stats)
    print()

    # ROLE 기반 분석
    print("=== ROLE 분석 ===")
    role_stats = analyze_role(df)
    print(role_stats)
    print()


if __name__ == "__main__":
    main()
