import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

# 전체 요청에 대한 동시 처리 제한 (10~20 추천)
# 너무 높으면 Riot 429 발생 → 10이 안전함
API_SEMAPHORE = asyncio.Semaphore(10)


async def safe_get_json(session, url, params=None, headers=None):
    """Riot API용 안전 JSON fetch (429 자동 재시도 + 세마포어 보호)"""

    async with API_SEMAPHORE:
        while True:
            try:
                async with session.get(url, params=params, headers=headers) as res:
                    # 429 요청 초과 → Retry-After 적용
                    if res.status == 429:
                        retry_after = float(res.headers.get("Retry-After", 1))
                        print(f"[429] Too Many Requests → {retry_after}s 대기")
                        await asyncio.sleep(retry_after)
                        continue

                    if res.status == 200:
                        return await res.json()

                    # 기타 오류
                    text = await res.text()
                    print(f"[오류] {res.status} : {text}")
                    return None

            except Exception as e:
                print(f"[요청 오류] {e}")
                await asyncio.sleep(1)
