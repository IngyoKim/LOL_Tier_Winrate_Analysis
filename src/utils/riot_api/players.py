from .riot_async import safe_get_json, API_KEY

REGION_PLATFORM = "kr"


async def fetch_players_by_tier(session, tier, division=None, page=1):
    tier = tier.upper()
    headers = {"X-Riot-Token": API_KEY}

    # MASTER~CHALLENGER (division 없음)
    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        ENDPOINTS = {
            "MASTER": "masterleagues",
            "GRANDMASTER": "grandmasterleagues",
            "CHALLENGER": "challengerleagues",
        }
        url = f"https://{REGION_PLATFORM}.api.riotgames.com/lol/league/v4/{ENDPOINTS[tier]}/by-queue/RANKED_SOLO_5x5"
        data = await safe_get_json(session, url, headers=headers)
        return data.get("entries", []) if data else []

    # IRON~DIAMOND (division 필요)
    if division is None:
        raise ValueError("IRON~DIAMOND tier requires division parameter.")

    url = f"https://{REGION_PLATFORM}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
    params = {"page": page}
    data = await safe_get_json(session, url, params=params, headers=headers)
    return data or []
