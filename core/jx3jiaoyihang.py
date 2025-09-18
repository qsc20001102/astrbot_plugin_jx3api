# core/jx3jiaoyihang.py
import requests
import json
from astrbot.api import logger
from urllib.parse import quote

def fetch_jx3_data(api_url=None, **params):
    # 函数实现
    try:
        response = requests.get(api_url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
          
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求出错: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return None



def fetch_jx3_jiaoyihang(inserver="眉间雪", inname="守缺"):

    # URL 编码
    encoded_text = quote(inname)
    
    custom_url = f"https://node.jx3box.com/item_merged/name/{encoded_text}"
    params = {
        "strictly": 0    
        }
    
    data = fetch_jx3_data(custom_url,**params)

    # 创建一个空列表来存储结果
    filtered_items = []
    
    # 遍历列表中的每个项目
    for item in data.get("list", []):
        # 提取id和Name字段
        filtered_item = {
            "id": item.get("id"),
            "Name": item.get("Name")
        }
        # 添加到结果列表
        filtered_items.append(filtered_item)

    # 提取所有ID
    ids = [item.get("id") for item in filtered_items]

    # 返回格式化结果
    stringids = ",".join(ids) if ids else ""

    custom_url = f"https://next2.jx3box.com/api/item-price/list"
    params = {
            "server": "眉间雪",  # 默认服务器
            "itemIds": "5_47129"  # 默认当天
        }
    
    # 接受传入的参数
    params["server"]=inserver
    params["itemIds"]=stringids

    data = fetch_jx3_data(custom_url,**params)

    logger.error(f"搜索到物品: \n{filtered_items}\n{params}")

    return data.get("data", "无交易行数据")
  
