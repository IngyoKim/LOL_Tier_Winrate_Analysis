def extract_match_rows(match_json):
    if match_json is None:
        return []

    info = match_json["info"]

    match_id = match_json["metadata"]["matchId"]
    game_duration = info["gameDuration"]
    participants = info["participants"]

    lane_order = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]

    team_players = {100: [], 200: []}
    for p in participants:
        team_players[p["teamId"]].append(p)

    for tid in [100, 200]:
        for idx, p in enumerate(team_players[tid]):
            p["_fixed_lane"] = lane_order[idx]

    lane_map = {}
    for p in participants:
        lane = p["_fixed_lane"]
        lane_map.setdefault(lane, []).append(p)

    rows = []
    for p in participants:
        team_id = p["teamId"]
        lane = p["_fixed_lane"]

        enemy_lane_champ = None
        for enemy in lane_map[lane]:
            if enemy["teamId"] != team_id:
                enemy_lane_champ = enemy["championName"]
                break

        rows.append({
            "matchId": match_id,
            "gameDuration": game_duration,
            "playerPuuid": p["puuid"],
            "teamId": team_id,
            "win": int(p["win"]),
            "lane": lane,
            "champion": p["championName"],
            "enemyLaneChampion": enemy_lane_champ,
        })

    return rows
