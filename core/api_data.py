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
    
    async def _make_request(self, method, url, params_data=None):
        """
        内部请求方法，统一处理请求逻辑
        
        Args:
            method: 请求方法 ('GET', 'POST')
            url: 请求URL
            params_data: 统一的参数字典，如 {"name": "万花"}
        
        Returns:
            成功时返回解析后的数据，失败返回None
        """
        timeout = ClientTimeout(total=self.base_timeout)
        
        try:
            # 添加请求日志
            logger.debug(f"发起 {method} 请求: {url}")
            logger.debug(f"参数数据: {params_data}")
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method.upper() == 'GET':
                    # GET请求：参数作为查询字符串
                    async with session.get(
                        url, 
                        params=params_data,
                        ssl=self.ssl_verify
                    ) as response:
                        return await self._handle_response(response)
                
                elif method.upper() == 'POST':
                    # POST请求：参数作为JSON数据
                    headers = {'Content-Type': 'application/json'}
                    async with session.post(
                        url,
                        json=params_data,  # 使用json参数而不是data
                        headers=headers,
                        ssl=self.ssl_verify
                    ) as response:
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
        处理HTTP响应
        
        Args:
            response: aiohttp响应对象
            
        Returns:
            解析后的数据或None
        """
        try:
            # 添加响应日志
            logger.debug(f"响应状态: {response.status}")
            
            response.raise_for_status()
            data = await response.json()
            
            logger.debug(f"响应数据: {data}")
            
            # 检查API响应状态
            return self._check_response_data(data)
            
        except aiohttp.ClientError as e:
            logger.error(f"HTTP错误: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            # 尝试读取原始文本内容
            try:
                text_content = await response.text()
                logger.error(f"原始响应内容: {text_content}")
            except:
                pass
            return None
    
    def _check_response_data(self, data):
        """
        检查API响应数据的通用逻辑
        
        Args:
            data: API返回的数据
            
        Returns:
            检查通过返回数据，否则返回None
        """
        # 如果数据是字符串，尝试解析为JSON
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.error("响应数据是无效的JSON字符串")
                return None
        
        # 检查是否有code字段
        if data and 'code' in data:
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
    
    async def post(self, api_url, params_data=None, outdata=None):
        """
        POST请求方法
        
        Args:
            api_url: API地址
            params_data: 参数字典，如 {"name": "万花"}
            outdata: 返回数据中要提取的字段
        
        Returns:
            成功时返回outdata字段的数据，失败返回None
        """
        data = await self._make_request('POST', api_url, params_data)
        
        if data is None:
            return None
            
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})
    
    async def get(self, api_url, params_data=None, outdata=None):
        """
        GET请求方法
        
        Args:
            api_url: API地址
            params_data: 参数字典，如 {"name": "万花"}
            outdata: 返回数据中要提取的字段
        
        Returns:
            成功时返回outdata字段的数据，失败返回None
        """
        data = await self._make_request('GET', api_url, params_data)
        
        if data is None:
            return None
            
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})


# 保持原有函数接口的兼容性
async def api_data_post(api_url, params_data=None, outdata=None):
    """兼容原有函数的POST请求"""
    client = APIClient()
    return await client.post(api_url, params_data, outdata)

async def api_data_get(api_url, params_data=None, outdata=None):
    """兼容原有函数的GET请求"""
    client = APIClient()
    return await client.get(api_url, params_data, outdata)