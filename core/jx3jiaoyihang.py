# core/jx3jiaoyihang.py
import requests
import json
from astrbot.api import logger
from urllib.parse import quote


#接口函数的实现
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


def fetch_all_pages(base_url, initial_params, max_pages=None):
    """
    获取所有分页数据
    
    Args:
        base_url: API基础URL
        initial_params: 初始请求参数
        max_pages: 最大页数限制（可选）
    
    Returns:
        list: 所有页面的数据列表
    """
    all_data = []
    current_page = 1
    
    while True:
        # 设置当前页码
        params = initial_params.copy()
        params["page"] = str(current_page)
        
        # 请求数据
        data = fetch_jx3_data(base_url, **params)
        
        if not data or "list" not in data:
            break
            
        # 添加当前页数据到总列表
        all_data.extend(data["list"])
        
        # 检查是否还有更多页面
        total_pages = data.get("pages", 1)
        if current_page >= total_pages:
            break
            
        # 检查是否达到最大页数限制
        if max_pages and current_page >= max_pages:
            break
            
        current_page += 1
        
    return all_data


def merge_item_data_by_itemid(price_items, item_list):
    """
    根据ItemId和id字段将物品名称信息合并到价格数据中
    
    Args:
        price_data: 第一组数据，包含价格信息的字典
        item_list_data: 第二组数据，包含物品列表信息的字典
    
    Returns:
        dict: 合并后的数据，包含价格和名称信息
    """
    
    
    # 创建一个字典用于快速查找物品名称，使用id作为键
    item_name_map = {}
    for item in item_list:
        item_id = item.get("id")
        item_name = item.get("Name")
        if item_id and item_name:
            item_name_map[item_id] = item_name
    
    # 创建一个新的结果字典
    merged_data = {"code": price_items.get("code", 0), "msg": price_items.get("msg", ""), "data": {}}
    
    # 遍历价格数据，添加名称信息
    for item_id, price_info in price_items.items():
        # 复制价格信息
        merged_item = price_info.copy()
        
        # 使用ItemId字段查找对应的名称
        item_id_to_match = merged_item.get("ItemId")
        if item_id_to_match and item_id_to_match in item_name_map:
            merged_item["Name"] = item_name_map[item_id_to_match]
        else:
            merged_item["Name"] = "未知物品"
        
        # 添加到结果中
        merged_data["data"][item_id] = merged_item
    
    return merged_data


#交易行数据查询函数
def fetch_jx3_jiaoyihang(inserver="眉间雪", inname="武技殊影图"):

    # URL 编码  
    custom_url = f"https://node.jx3box.com/item_merged/name/{quote(inname)}"
    params = {
        "client": "std",    # 默认客户端
        "strict": "0" ,  # 默认模糊搜索
        "page": "1",    # 默认第一页
        "per": "50"   # 默认每页50条
        }
    
    #请求接口获取物品ID
    data_item = fetch_jx3_data(custom_url,**params)

    # 检查是否获取到数据
    if not data_item or "list" not in data_item:
        logger.error(f"未找到物品: {inname}")
        return "无交易行数据"
    
    # 创建一个空列表来存储结果
    data_item_list = data_item.get("list", [])

    # 提取所有ID
    ids = [item.get("id") for item in data_item_list]

    # 返回格式化结果
    stringids = ",".join(ids) if ids else ""

    custom_url = f"https://next2.jx3box.com/api/item-price/list"
    params = {
            "server": "眉间雪",  # 默认服务器
            "itemIds": "5_47129"  # 默认物品ID
        }
    
    # 接受传入的参数
    params["server"]=inserver
    params["itemIds"]=stringids

    #请求接口获取物品交易行数据
    data_price = fetch_jx3_data(custom_url,**params)

    merged_data = merge_item_data_by_itemid(data_price.get("data", []), data_item_list)

    # 打印日志
    logger.info(f"搜索到物品: \n{inname}\n{merged_data}\n{params}")
    
    return merged_data.get("data", "无交易行数据")
  
