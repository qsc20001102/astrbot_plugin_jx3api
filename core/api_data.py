# core/request.py
import requests
import json
from astrbot.api import logger

def api_data_post(api_url, json_data=None, outdata=None):
    """
    获取数据的POST请求函数
    
    Args:
        api_url: API地址
        json_data: POST请求的JSON数据
        outdata: 返回数据中要提取的字段
    
    Returns:
        成功时返回outdata字段的数据，失败返回None
    """
    try:
        response = requests.post(api_url, json=json_data, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
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
        
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return None
    
def api_data_get(api_url,params=None,outdata=None):
    """
    获取数据的GET请求函数
    
    Args:
        api_url: API地址
        
        params: 其他查询参数
    
    Returns:
        成功时返回outdata字段的数据，失败返回None
    """
    try:
        response = requests.get(api_url, params, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
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
        
        if outdata is None or outdata == "":
            return data
        return data.get(outdata, {})
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return None