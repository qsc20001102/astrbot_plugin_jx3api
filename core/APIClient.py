# core/request.py
import aiohttp
import json
from aiohttp import ClientTimeout
from astrbot.api import logger

class APIClient:
    """
    API客户端类，支持GET/POST请求，同时兼容JSON和二进制数据
    """
    
    def __init__(self, base_timeout=10, ssl_verify=False):
        self.base_timeout = base_timeout
        self.ssl_verify = ssl_verify

    async def _make_request(self, method, url, params_data=None):
        timeout = ClientTimeout(total=self.base_timeout)
        try:
            logger.debug(f"发起 {method} 请求: {url}")
            logger.debug(f"参数数据: {params_data}")
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method.upper() == 'GET':
                    async with session.get(url, params=params_data, ssl=self.ssl_verify) as response:
                        return await self._handle_response(response)
                elif method.upper() == 'POST':
                    headers = {'Content-Type': 'application/json'}
                    async with session.post(url, json=params_data, headers=headers, ssl=self.ssl_verify) as response:
                        return await self._handle_response(response)
                else:
                    logger.error(f"不支持的HTTP方法: {method}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"请求出错: {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None

    async def _handle_response(self, response):
        """
        处理响应：支持 JSON 和二进制数据
        """
        try:
            logger.debug(f"响应状态: {response.status}")
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')

            if 'image' in content_type or 'octet-stream' in content_type:
                # 返回二进制数据
                data = await response.read()
                return data

            # 尝试解析为 JSON
            try:
                data = await response.json(content_type=None)
            except Exception:
                text = await response.text()
                logger.debug(f"原始文本响应: {text}")
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    logger.error("无法解析为 JSON 数据")
                    return None

            logger.debug(f"响应数据: {data}")
            return self._check_response_data(data)
        except aiohttp.ClientError as e:
            logger.error(f"HTTP错误: {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None

    def _check_response_data(self, data):
        """
        检查 API 返回 JSON 数据
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.error("响应数据是无效的JSON字符串")
                return None

        if data and isinstance(data, dict) and 'code' in data:
            if data.get('code') not in [200, "0", 0, 1]:
                logger.error(f"API返回错误:{data.get('code', '未知状态')} {data.get('msg', '未知错误')}")
                return None
        elif not data:
            logger.error("API返回空数据")
            return None

        return data

    async def post(self, api_url, params_data=None, outdata=None):
        data = await self._make_request('POST', api_url, params_data)
        if data is None:
            return None
        if isinstance(data, bytes):
            return data
        if not outdata:
            return data
        return data.get(outdata, {})

    async def get(self, api_url, params_data=None, outdata=None):
        data = await self._make_request('GET', api_url, params_data)
        if data is None:
            return None
        if isinstance(data, bytes):
            return data
        if not outdata:
            return data
        return data.get(outdata, {})

    async def all_pages(self, http, api_url, params_data=None, outdata: str = "", listdata: str = "list", max_pages: int = 10):
        all_data = []
        current_page = 1
        while True:
            params = params_data.copy() if params_data else {}
            params["page"] = str(current_page)

            if http.upper() == "POST":
                data = await self.post(api_url, params, outdata)
            else:
                data = await self.get(api_url, params, outdata)

            if not data or isinstance(data, bytes):
                # 二进制数据或者空数据，不分页
                break

            if not data.get(listdata):
                break

            all_data.extend(data[listdata])

            if max_pages and current_page >= max_pages:
                break

            current_page += 1
            logger.info(f"已获取第 {current_page} 页数据")
        return all_data

# 保持原接口兼容
async def api_data_post(api_url, params_data=None, outdata=None):
    client = APIClient()
    return await client.post(api_url, params_data, outdata)

async def api_data_get(api_url, params_data=None, outdata=None):
    client = APIClient()
    return await client.get(api_url, params_data, outdata)
