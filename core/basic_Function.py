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
    

def extract_field(data_list, field_name):
    """
    从列表中的字典提取指定字段的所有值

    Args:
        data_list (list): 数据列表，每个元素是 dict
        field_name (str): 要提取的字段名

    Returns:
        list: 提取出来的字段值列表
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