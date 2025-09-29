# core/jx3jiaoyihang.py
from astrbot.api import logger
from urllib.parse import quote
from datetime import datetime

from .class_reqsest import api_data_get, api_data_post


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
        data = api_data_get(base_url, params)
        
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


def merge_item_data_by_itemid(price_data, item_list_data):
    """
    根据ItemId和id字段将物品名称信息合并到价格数据中
    
    Args:
        price_data: 第一组数据，包含价格信息的字典
        item_list_data: 第二组数据，可以是字典（包含"list"键）或直接是物品列表
    
    Returns:
        dict: 合并后的数据，包含价格和名称信息
    """
    # 提取价格数据中的物品信息
    price_items = price_data.get("data", {})
    
    # 处理不同类型的item_list_data输入
    if isinstance(item_list_data, dict) and "list" in item_list_data:
        # 如果是字典且包含"list"键
        item_list = item_list_data.get("list", [])
    elif isinstance(item_list_data, list):
        # 如果直接是列表
        item_list = item_list_data
    else:
        # 其他情况，使用空列表
        item_list = []
    
    # 创建一个字典用于快速查找物品名称，使用id作为键
    item_name_map = {}
    for item in item_list:
        item_id = item.get("id")
        item_name = item.get("Name")
        if item_id and item_name:
            item_name_map[item_id] = item_name
    
    # 创建一个新的结果字典
    merged_data = {"code": price_data.get("code", 0), "msg": price_data.get("msg", ""), "data": {}}
    
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
def jx3_data_jiaoyihang(inserver="眉间雪", inname="武技殊影图"):
    """
    获取剑三交易行某区某物品价格数据
    
    Args:
        inserver: 第一组数据，服务器名称
        inname: 物品名称
    
    Returns:
        list: 合并后的数据，包含价格和名称信息
    """
    # 第一步：获取所有物品列表数据（处理分页）
    custom_url = f"https://node.jx3box.com/item_merged/name/{quote(inname)}"
    initial_params = {
        "client": "std",
        "strict": "0",
        "per": "50"  # 每页数量，可以根据需要调整
    }
    
    # 获取所有页面的物品数据
    all_items = fetch_all_pages(custom_url, initial_params)
    
    if not all_items:
        #logger.error(f"未找到物品: {inname}")
        return "未找到改物品"
    
    # 提取所有ID
    ids = [item.get("id") for item in all_items if item.get("id")]
    
    if not ids:
        #logger.error(f"物品 {inname} 没有有效的ID")
        return "未找到改物品"
    
    # 返回格式化结果
    stringids = ",".join(ids)
    logger.info(f"搜索到物品: {inname}, 共找到 {len(ids)} 个物品\nIDs: {stringids}")
    
    # 第二步：获取价格数据
    price_url = "https://next2.jx3box.com/api/item-price/list"
    price_params = {
        "server": inserver,
        "itemIds": stringids
    }
    
    price_data = api_data_get(price_url, price_params)
    
    if not price_data or "data" not in price_data:
        return "无交易行数据"
    
    if not price_data["data"] or (isinstance(price_data["data"], dict) and not price_data["data"]) or (isinstance(price_data["data"], list) and not price_data["data"]):
        return "无交易行数据"
    
    # 第三步：合并数据
    merged_data = merge_item_data_by_itemid(price_data, {"list": all_items})
    
    # 处理合并后的数据
    result_items = []
    for item_id, item_info in merged_data.get("data", {}).items():
        # 格式化价格（假设价格是以铜钱为单位，转换为金）
        lowest_price = item_info.get("LowestPrice", 0)
        bricks = lowest_price // 100000000 if lowest_price else 0
        gold = (lowest_price % 100000000) // 10000 if lowest_price else 0
        silver = (lowest_price % 10000) // 100 if lowest_price else 0
        copper = lowest_price % 100 if lowest_price else 0
        
        price_str = f"{bricks}砖{gold}金{silver}银{copper}铜" if lowest_price else "无价格"
        
        result_items.append({
            "name": item_info.get("Name", "未知物品"),
            "price": price_str,
            "avg_price": item_info.get("AvgPrice", 0),
            "sample_size": item_info.get("SampleSize", 0)
        })
    
    # 按价格排序
    result_items.sort(key=lambda x: x["avg_price"])
    
    return result_items
  