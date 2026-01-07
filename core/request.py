# core/request.py
import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any, Union, List
from aiohttp import ClientTimeout, ClientSession

from astrbot.api import logger

class APIClient:
    """
    API客户端类
    
    优化说明：
    1. 复用 aiohttp.ClientSession 以提高性能。
    2. 增加类型提示 (Type Hints)。
    3. 支持异步上下文管理器 (Async Context Manager)。
    """

    def __init__(self, base_timeout: int = 10, ssl_verify: bool = False):
        self.base_timeout = base_timeout
        self.ssl_verify = ssl_verify
        self._session: Optional[ClientSession] = None

    async def get_session(self) -> ClientSession:
        """获取或创建单例 Session"""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self.base_timeout)
            self._session = ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """关闭 Session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        await self.get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request(self, method: str, url: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Any:
        """
        统一的内部请求处理方法
        """
        session = await self.get_session()
        method = method.upper()
        
        # 记录日志
        logger.debug(f"发起 {method} 请求: {url}")
        if params: logger.debug(f"Query参数: {params}")
        if json_data: logger.debug(f"Body数据: {json_data}")

        try:
            # aiohttp 会自动处理 json=json_data 时的 Content-Type
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                ssl=self.ssl_verify
            ) as response:
                return await self._handle_response(response)
                
        except aiohttp.ClientError as e:
            logger.error(f"网络请求出错 ({method} {url}): {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误 ({method} {url}): {e}")
            return None

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """处理响应：自动识别二进制或JSON"""
        try:
            logger.debug(f"响应状态: {response.status}")
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()

            if 'image' in content_type or 'octet-stream' in content_type:
                return await response.read()

            try:
                data = await response.json()
            except Exception:
                text = await response.text()
                try:
                    loop = asyncio.get_running_loop()
                    data = await loop.run_in_executor(None, json.loads, text)
                except json.JSONDecodeError:
                    logger.error(f"无法解析响应为 JSON。原始内容: {text[:100]}...")
                    return None

            logger.debug(f"响应数据: {data}")
            return self._validate_api_payload(data)

        except aiohttp.ClientError as e:
            logger.error(f"HTTP响应错误: {e}")
            return None

    def _validate_api_payload(self, data: Any) -> Any:
        """校验业务层面的 JSON 数据结构"""
        if not data:
            logger.error("API返回空数据")
            return None

        # 如果返回的是 JSON 字符串而非对象，再次解析
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return None
        
        if isinstance(data, dict) and 'code' in data:
            # 兼容多种成功状态码：200, "0", 0, 1
            code = data.get('code')
            if code not in [200, "0", 0, 1]:
                msg = data.get('msg') or data.get('message', '未知错误')
                logger.error(f"API业务报错: code={code}, msg={msg}")
                return None
        
        return data

    async def get(self, url: str, params: Optional[Dict] = None, out_key: Optional[str] = None) -> Any:
        """GET 请求封装"""
        data = await self._request('GET', url, params=params)
        return self._extract_data(data, out_key)

    async def post(self, url: str, data: Optional[Dict] = None, out_key: Optional[str] = None) -> Any:
        """POST 请求封装 (默认发送 JSON)"""
        data = await self._request('POST', url, json_data=data)
        return self._extract_data(data, out_key)

    def _extract_data(self, data: Any, key: Optional[str]) -> Any:
        """辅助方法：从结果中提取指定字段"""
        if data is None:
            return None
        if isinstance(data, bytes):
            return data
        if key and isinstance(data, dict):
            return data.get(key, {})
        return data

    async def all_pages(
        self, 
        method: str, 
        url: str, 
        params_data: Optional[Dict] = None, 
        out_key: str = "", 
        list_key: str = "list", 
        max_pages: int = 10
    ) -> List[Any]:
        """
        分页获取所有数据
        :param method: GET 或 POST
        :param list_key: 列表数据在 JSON 中的字段名，如 'data' 或 'list'
        """
        all_data = []
        current_page = 1
        params = params_data.copy() if params_data else {}

        while True:
            params["page"] = str(current_page)
            
            if method.upper() == "POST":
                data = await self.post(url, data=params, out_key=out_key)
            else:
                data = await self.get(url, params=params, out_key=out_key)

            # 终止条件判断
            if not data or isinstance(data, bytes):
                break
            
            # 如果 data 是列表本身（有些API直接返回列表）
            page_items = data if isinstance(data, list) else data.get(list_key)
            
            if not page_items:
                break

            all_data.extend(page_items)

            if current_page >= max_pages:
                break

            current_page += 1
            logger.info(f"已获取第 {current_page} 页数据")

        return all_data