# core/request.py
import aiohttp
import json
from aiohttp import ClientTimeout
from astrbot.api import logger

class APIClient:
    """
    API客户端类，封装GET和POST请求功能
    """
    
    def __init__(self, base_timeout=10, ssl_verify=False):
        """
        初始化APIClient
        
        Args:
            base_timeout: 默认超时时间（秒）
            ssl_verify: SSL证书验证开关
        """
        self.base_timeout = base_timeout
        self.ssl_verify = ssl_verify
    
    async def _make_request(self, method, url, **kwargs):
        """
        内部请求方法，处理通用请求逻辑
        
        Args:
            method: 请求方法 ('GET', 'POST')
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            成功时返回解析后的数据，失败返回None
        """
        timeout = ClientTimeout(total=self.base_timeout)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(method, url, ssl=self.ssl_verify, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # 检查API响应状态
                    return self._check_response_data(data)
                    
        except aiohttp.ClientError as e:
            logger.error(f"请求出错: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None
    
    def _check_response_data(self, data):
        """
        检查API响应数据的通用逻辑
        
        Args:
            data: API返回的数据
            
        Returns:
            检查通过返回数据，否则返回None
        """
        # 检查是否有code字段
        if 'code' in data:
            # 有code字段时，检查是否成功
            if data.get('code') not in [200, "0", 0]:
                logger.error(f"API返回错误:{data.get('code', '未知状态')} {data.get('msg', '未知错误')}")
                return None
        else:
            # 无code字段时，检查数据是否为空
            if not data:
                logger.error("API返回空数据")
                return None
        
        return data
    
    async def post(self, api_url, json_data=None, outdata=None):
        """
        POST请求方法
        
        Args:
            api_url: API地址
            json_data: POST请求的JSON数据
            outdata: 返回数据中要提取的字段
        
        Returns:
            成功时返回outdata字段的数据，失败返回None
        """
        data = await self._make_request('POST', api_url, json=json_data)
        
        if data is None:
            return None
            
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})
    
    async def get(self, api_url, params=None, outdata=None):
        """
        GET请求方法
        
        Args:
            api_url: API地址
            params: 其他查询参数
            outdata: 返回数据中要提取的字段
        
        Returns:
            成功时返回outdata字段的数据，失败返回None
        """
        data = await self._make_request('GET', api_url, params=params)
        
        if data is None:
            return None
            
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})

    async def request(self, api_config, outdata=None):
        """
        通用请求方法，根据api_config中的method选择GET或POST
        
        Args:
            api_config: 包含url, method, params/json等信息的字典
            outdata: 返回数据中要提取的字段
        
        Returns:
            成功时返回outdata字段的数据，失败返回None
        """
        if 'url' not in api_config or 'method' not in api_config:
            logger.error("api_config必须包含url和method字段")
            return None
        data = await self._make_request(api_config['method'], api_config['url'], params=api_config['params'])
        
        if data is None:
            return None
            
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})









# 保持原有函数接口的兼容性（可选）
async def api_data_post(api_url, json_data=None, outdata=None):
    """兼容原有函数的POST请求"""
    client = APIClient()
    return await client.post(api_url, json_data, outdata)

async def api_data_get(api_url, params=None, outdata=None):
    """兼容原有函数的GET请求"""
    client = APIClient()
    return await client.get(api_url, params, outdata)