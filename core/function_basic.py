import os
from pathlib import Path

def load_template(template_name):
    """
    从模板文件加载模板内容
    
    Args:
        template_name: 模板文件名（不带路径）
    
    Returns:
        str: 模板内容
    """
    # 获取模板文件路径
    plugin_dir = Path(__file__).parent.parent
    template_path = plugin_dir / "templates" / template_name
    
    # 检查文件是否存在
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")
    
    # 读取模板内容
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()
    

def flatten_field(data_list, field_name):
    """
    提取并扁平化指定字段的值

    从一个字典列表中，收集指定字段的所有值。
    如果字段的值是列表，则会被展开（扁平化）加入结果；
    如果字段的值是单个元素，则直接加入结果。

    Args:
        data_list (list[dict]): 数据列表，每个元素是字典
        field_name (str): 要提取的字段名

    Returns:
        list: 扁平化后的字段值列表
    """
    extracted_data = []
    for item in data_list:
        if field_name in item and item[field_name]:
            # 如果是 list，展开
            if isinstance(item[field_name], list):
                extracted_data.extend(item[field_name])
            else:
                extracted_data.append(item[field_name])
    return extracted_data


def extract_fields(data_list, fields):
    """
    从字典列表中提取多个字段

    Args:
        data_list (list[dict]): 包含字典的列表
        fields (list[str]): 要提取的字段名列表

    Returns:
        list[dict]: 只包含指定字段的新字典列表
    """
    result = []
    try:
        for item in data_list:
            extracted = {field: item.get(field) for field in fields}
            result.append(extracted)
    except Exception as e:
        print(f"提取字段时出错: {e}")
        return []
    return result


def extract_field(data_list, field_name):
    """
    从列表中的字典提取指定字段的所有值

    Args:
        data_list (list): 数据列表，每个元素是 dict
        field_name (str): 要提取的字段名

    Returns:
        list: 提取出来的字段值列表
    """
    return [item[field_name] for item in data_list if field_name in item]


def gold_to_string(gold_amount):
    """
    将金钱数值转换为字符串表示形式

    Args:
        gold_amount (int): 金钱数值，单位为铜币

    Returns:
        str: 格式化后的金钱字符串，例如 "1金2银3铜"
    """
    bricks = gold_amount // 100000000 if gold_amount else 0
    gold = (gold_amount % 100000000) // 10000 if gold_amount else 0
    silver = (gold_amount % 10000) // 100 if gold_amount else 0
    copper = gold_amount % 100 if gold_amount else 0
        
    gold_str = f"{bricks}砖{gold}金{silver}银{copper}铜" if gold_amount else "无价格"

    return gold_str