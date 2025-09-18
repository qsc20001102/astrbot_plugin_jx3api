# core/request.py
import requests
import json
from astrbot.api import logger

def fetch_jx3_data(api_url=None,outdata="data", **params):
    # 函数实现
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
