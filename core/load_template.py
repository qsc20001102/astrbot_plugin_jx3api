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