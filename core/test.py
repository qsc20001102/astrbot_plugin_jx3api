import aiohttp
import asyncio

async def fetch_data():
    url = "https://trade-api.seasunwbl.com/api/buyer/goods/list?filter%255Bstate%255D=1&page=1&size=10&goods_type=3&sort%255Bprice%255D=1&filter%255Brole_appearance%255D=%25E6%25BB%2587%25E6%259E%2597%25E9%259B%25A8%25C2%25B7%25E7%259F%25A5%25E5%258D%2597%25C2%25B7%25E6%25A0%2587%25E5%2587%2586"
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': 'trade-api.seasunwbl.com',
        'Connection': 'keep-alive',
        'Cookie': 'ts_session_id=AqvN1gha8NDXTjdauL6ApVT4KgbJLvPv0Dnd9uid; ts_session_id_=AqvN1gha8NDXTjdauL6ApVT4KgbJLvPv0Dnd9uid'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.text()
            print(data)

# Run the async function
asyncio.run(fetch_data())
