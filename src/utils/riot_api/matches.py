from .riot_async import safe_get_json, API_KEY

REGION_ROUTING = "asia"


async def fetch_match_ids(session, puuid, count=20):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    headers = {"X-Riot-Token": API_KEY}
    return await safe_get_json(session, url, params=params, headers=headers)


async def fetch_match_info(session, match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}
    return await safe_get_json(session, url, headers=headers)
