from .riot_async import safe_get_json, API_KEY

REGION_ROUTING = "asia"


async def fetch_match_timeline(session, match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    headers = {"X-Riot-Token": API_KEY}
    return await safe_get_json(session, url, headers=headers)
