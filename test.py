import datetime
import hashlib
import hmac
import json
import httpx
 
def format_body(data: dict) -> str:
    return json.dumps(data, separators=(',', ':'))
 
 
def gen_ts() -> str:
    return f"{datetime.datetime.now():%Y%m%d%H%M%S%f}"[:-3]
 
 
def gen_xsk(data: str) -> str:
    data += "@#?.#@"
    secret = "MaYoaMQ3zpWJFWtN9mqJqKpHrkdFwLd9DDlFWk2NnVR1mChVRI6THVe6KsCnhpoR"
    return hmac.new(secret.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()
 
async def post_url(url, proxy: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        resp = await client.post(url, timeout = timeout, headers = headers, data = data)
        result = resp.text
        return result
 
async def get_arena_data(token: str) -> dict:
    param = {
        "gameVersion":0,
        "forceId":-1,
        "zone": "",
        "server": "",
        "ts": gen_ts()
    }
    param = format_body(param)
    device_id = token.split("::")[1]
    headers = {
        'Host': 'm.pvp.xoyo.com',
        'accept': 'application/json',
        'deviceid': device_id,
        'platform': 'ios',
        'gamename': 'jx3',
        'clientkey': '1',
        'cache-control': 'no-cache',
        'apiversion': '1',
        'sign': 'true',
        'token': token,
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
        'User-Agent': 'SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0',
        "x-sk": gen_xsk(param)
    }
    data = await post_url(url="https://w.pvp.xoyo.com/api/h5/parser/cd-process/get-by-role", data=param, headers=headers)
    return json.loads(data)
 
if __name__ == "__main__":
    import asyncio
    token = input()
    ans = asyncio.run(get_arena_data(token))
    print(ans)