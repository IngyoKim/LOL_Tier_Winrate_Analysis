"""
extension_timeline.py
1분 단위 timeline diff 생성

추가 포함:
- baronDiff
- atakhanDiff
- elderDiff
- grubDiff (HORDE / VOID_GRUB / VOID_LARVA)
- outerTowerDiff / innerTowerDiff / baseTowerDiff / nexusTowerDiff
- inhibitorDiff
"""

def extract_timeline_features(match_json: dict, timeline_json: dict):

    info = match_json["info"]
    match_id = match_json["metadata"]["matchId"]
    game_duration = info["gameDuration"]  # seconds

    frames = timeline_json["info"]["frames"]
    frame_interval = timeline_json["info"].get("frameInterval", 60000)

    total_minutes = game_duration // 60

    # 프레임 간격이 0이면 timeline이 깨진 경기 → 분석 불가 (skip)
    if not frame_interval or frame_interval == 0:
        print(f"[경고] frameInterval=0 → timeline 분석 불가: {match_id}")
        return None

    def minute_to_frame(minute):
        return int((minute * 60000) / frame_interval)

    max_frame = len(frames) - 1

    def safe_frame(minute):
        idx = minute_to_frame(minute)
        return frames[min(idx, max_frame)]

    # participantId → teamId
    participants = match_json["info"]["participants"]
    pid_to_team = {p["participantId"]: p["teamId"] for p in participants}

    # ---------------------------------------------------
    # Team Identification (Champion kill 기준)
    # ---------------------------------------------------
    def event_team(event):
        killer = event.get("killerId", 0)
        if killer == 0:
            return None
        return pid_to_team.get(killer, None)

    # ---------------------------------------------------
    # Gold/Kill 계산
    # ---------------------------------------------------
    def frame_gold_kills(frame):
        pf = frame["participantFrames"]

        t100_gold = t200_gold = 0
        for pid_str, pdata in pf.items():
            pid = int(pid_str)
            team = pid_to_team[pid]
            gold = pdata["totalGold"]

            if team == 100: 
                t100_gold += gold
            else:
                t200_gold += gold

        t100_kill = t200_kill = 0
        for ev in frame.get("events", []):
            if ev["type"] == "CHAMPION_KILL":
                t = event_team(ev)
                if t == 100:
                    t100_kill += 1
                elif t == 200:
                    t200_kill += 1

        return t100_gold, t200_gold, t100_kill, t200_kill

    # ---------------------------------------------------
    # Monsters: Dragon / Elder / Herald / Baron / Atakhan / Grub
    # ---------------------------------------------------
    def scan_monsters(minute):
        target_ms = minute * 60 * 1000

        d100 = d200 = 0
        e100 = e200 = 0
        h100 = h200 = 0
        b100 = b200 = 0
        a100 = a200 = 0
        g100 = g200 = 0  # Grub / Larva / Horde

        for frame in frames:
            for ev in frame.get("events", []):
                ts = ev.get("timestamp", 0)
                if ts > target_ms:
                    continue

                etype = ev.get("type")

                if etype == "ELITE_MONSTER_KILL":
                    team = ev.get("killerTeamId")
                    mtype = ev.get("monsterType")
                    msub = ev.get("monsterSubType")

                    # ----- Elder Dragon (중요: monsterSubType으로만 구분됨) -----
                    if msub == "ELDER_DRAGON":
                        if team == 100: 
                            e100 += 1
                        else: 
                            e200 += 1

                    # ----- Normal Dragons -----
                    elif mtype == "DRAGON":
                        if team == 100: 
                            d100 += 1
                        else: 
                            d200 += 1

                    # Herald
                    elif mtype == "RIFTHERALD":
                        if team == 100:
                            h100 += 1
                        else:
                            h200 += 1

                    # Baron
                    elif mtype == "BARON_NASHOR":
                        if team == 100:
                            b100 += 1
                        else:
                            b200 += 1

                    # Atakhan
                    elif mtype == "ATAKHAN":
                        if team == 100:
                            a100 += 1
                        else:
                            a200 += 1

                    # Grub / Horde (신규 패치)
                    elif mtype == "HORDE":
                        if team == 100:
                            g100 += 1
                        else:
                            g200 += 1

                # Legacy Grub (VOID_GRUB / VOID_LARVA)
                elif etype == "KILL_PREDEFINED_TARGET":
                    kill_type = ev.get("killType") or ev.get("predefinedTargetId")
                    if kill_type in ("VOID_GRUB", "VOID_LARVA"):
                        team = ev.get("killerTeamId") or ev.get("teamId")
                        if team == 100:
                            g100 += 1
                        else:
                            g200 += 1

        return d100, d200, e100, e200, h100, h200, b100, b200, a100, a200, g100, g200

    # ---------------------------------------------------
    # Buildings
    # ---------------------------------------------------
    def scan_buildings(minute):
        target_ms = minute * 60 * 1000

        out100 = out200 = 0
        inn100 = inn200 = 0
        base100 = base200 = 0
        nex100 = nex200 = 0
        inh100 = inh200 = 0

        for frame in frames:
            for ev in frame.get("events", []):
                ts = ev.get("timestamp", 0)
                if ts > target_ms:
                    continue

                if ev.get("type") != "BUILDING_KILL":
                    continue

                team = ev.get("teamId")
                btype = ev.get("buildingType")
                ttype = ev.get("towerType")

                if btype == "TOWER_BUILDING":
                    if ttype == "OUTER_TURRET":
                        if team == 100: out100 += 1
                        else: out200 += 1

                    elif ttype == "INNER_TURRET":
                        if team == 100: inn100 += 1
                        else: inn200 += 1

                    elif ttype == "BASE_TURRET":
                        if team == 100: base100 += 1
                        else: base200 += 1

                    elif ttype == "NEXUS_TURRET":
                        if team == 100: nex100 += 1
                        else: nex200 += 1

                elif btype == "INHIBITOR_BUILDING":
                    if team == 100: inh100 += 1
                    else: inh200 += 1

        return out100, out200, inn100, inn200, base100, base200, nex100, nex200, inh100, inh200

        # ---------------------------------------------------
    # Build CSV Row
    # ---------------------------------------------------
    result = {
        "matchId": match_id,
        "gameDuration": game_duration,
        "maxMinute": total_minutes
    }

    for minute in range(total_minutes + 1):

        # gold, kill
        g100, g200, k100, k200 = frame_gold_kills(safe_frame(minute))

        # monsters
        d100, d200, e100, e200, h100, h200, b100, b200, a100, a200, gr100, gr200 = scan_monsters(minute)

        # buildings
        out100, out200, inn100, inn200, base100, base200, nex100, nex200, inh100, inh200 = scan_buildings(minute)

        # --------------------------
        # Gold / Kills (team별 + diff)
        # --------------------------
        result[f"gold100_{minute}"] = g100
        result[f"gold200_{minute}"] = g200
        result[f"goldDiff_{minute}"] = g100 - g200

        result[f"kill100_{minute}"] = k100
        result[f"kill200_{minute}"] = k200
        result[f"killDiff_{minute}"] = k100 - k200

        # --------------------------
        # Monsters (team별 + diff)
        # --------------------------
        result[f"dragon100_{minute}"] = d100
        result[f"dragon200_{minute}"] = d200
        result[f"dragonDiff_{minute}"] = d100 - d200

        result[f"elder100_{minute}"] = e100
        result[f"elder200_{minute}"] = e200
        result[f"elderDiff_{minute}"] = e100 - e200

        result[f"herald100_{minute}"] = h100
        result[f"herald200_{minute}"] = h200
        result[f"heraldDiff_{minute}"] = h100 - h200

        result[f"baron100_{minute}"] = b100
        result[f"baron200_{minute}"] = b200
        result[f"baronDiff_{minute}"] = b100 - b200

        result[f"atakhan100_{minute}"] = a100
        result[f"atakhan200_{minute}"] = a200
        result[f"atakhanDiff_{minute}"] = a100 - a200

        result[f"grub100_{minute}"] = gr100
        result[f"grub200_{minute}"] = gr200
        result[f"grubDiff_{minute}"] = gr100 - gr200

        # --------------------------
        # Buildings (team별 + diff)
        # --------------------------
        result[f"outerTower100_{minute}"] = out100
        result[f"outerTower200_{minute}"] = out200
        result[f"outerTowerDiff_{minute}"] = out100 - out200

        result[f"innerTower100_{minute}"] = inn100
        result[f"innerTower200_{minute}"] = inn200
        result[f"innerTowerDiff_{minute}"] = inn100 - inn200

        result[f"baseTower100_{minute}"] = base100
        result[f"baseTower200_{minute}"] = base200
        result[f"baseTowerDiff_{minute}"] = base100 - base200

        result[f"nexusTower100_{minute}"] = nex100
        result[f"nexusTower200_{minute}"] = nex200
        result[f"nexusTowerDiff_{minute}"] = nex100 - nex200

        result[f"inhibitor100_{minute}"] = inh100
        result[f"inhibitor200_{minute}"] = inh200
        result[f"inhibitorDiff_{minute}"] = inh100 - inh200

    return result
