import os
import base64
import matplotlib.pyplot as plt

from pathlib import Path
from io import BytesIO
from datetime import datetime,date

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
    if not gold_amount:
        return "无价格"

    parts = []
    started = False  # 标记是否已经遇到第一个非零位

    bricks = gold_amount // 100000000
    gold = (gold_amount % 100000000) // 10000
    silver = (gold_amount % 10000) // 100
    copper = gold_amount % 100

    for value, unit in [(bricks, "砖"), (gold, "金"), (silver, "银"), (copper, "铜")]:
        if value != 0:
            started = True
        if started:
            parts.append(f"{value}{unit}")

    return "".join(parts)


def plot_line_chart_base64(data, x_field, y_field, title=None, reverse_x=False):
    """
    根据列表数据绘制折线图，返回 base64 图片字符串。
    
    :param data: list[dict] 数据列表
    :param x_field: str X轴字段
    :param y_field: str Y轴字段
    :param title: str 图表标题（可选）
    :param reverse_x: bool 是否反转 X 轴方向（默认 False：从左往右；True：从右往左）
    :return: str base64 图片字符串，可直接放到 <img src="..."> 中
    """
    if not data:
        raise ValueError("数据列表不能为空")

    # 字体设置（支持中文）
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 提取 X / Y 数据
    x_values = [str(item.get(x_field, "")) for item in data]
    y_values = [float(item.get(y_field, 0)) for item in data]

    # 创建画布
    plt.figure(figsize=(8, 5))
    plt.plot(x_values, y_values, marker='o', color='#4a90e2', linewidth=2)

    # 反转 X 轴
    if reverse_x:
        plt.gca().invert_xaxis()

    # 标题与标签
    if title is None:
        title = f"{y_field} 折线图"

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=30)
    plt.tight_layout()

    # 转 Base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    plt.close()

    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


def week_to_num(week :str):
    week_map = {
    "一": 0,
    "二": 1,
    "三": 2,
    "四": 3,
    "五": 4,
    "六": 5,
    "日": 6,  
    }
    return week_map.get(week,None)

def compare_date_str(date_str: str) -> str:
    """
    date_str 格式：YYYY-MM-DD
    """
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = date.today()

    if d < today:
        return "过去"
    elif d == today:
        return "今天"
    else:
        return "将来"