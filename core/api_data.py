# core/request.py
import requests
import json
from astrbot.api import logger

def api_data(api_url, json_data=None, outdata="data"):
    """
    获取数据的POST请求函数
    
    Args:
        api_url: API地址
        json_data: POST请求的JSON数据
        outdata: 返回数据中要提取的字段，默认为"data"
    
    Returns:
        成功时返回outdata字段的数据，失败返回None
    """
    try:
        response = requests.post(
            api_url, 
            json=json_data,  # JSON body数据
            timeout=10, 
            verify=False
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') not in [200, "0"]:
            logger.error(f"API返回错误: {data.get('msg', '未知错误')}")
            return None
        
        return data.get(outdata, {})
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return None
    
def fetch_jx3_data(api_url=None,outdata="data", **params):
    """
    获取数据的GET请求函数
    
    Args:
        api_url: API地址
        outdata: 返回数据中要提取的字段，默认为"data"
        **params: 其他查询参数
    
    Returns:
        成功时返回outdata字段的数据，失败返回None
    """
    try:
        response = requests.get(api_url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != 200:
            logger.error(f"API返回错误: {data.get('msg', '未知错误')}")
            return None
        
        return data.get(outdata, {})
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return None