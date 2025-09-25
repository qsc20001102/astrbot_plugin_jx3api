import pymysql
import time
from astrbot.api import logger
from .api_data import api_data_get, api_data_post


#连接数据库配置
db_config = {
    'host': '154.201.70.116',
    'port': 3306,
    'user': 'asrtbot',
    'password': 'qsc123456',
    'database': 'asrtbot',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor   #返回字典格式数据
}

# 提取所有 dataModels 中的数据
def extract_data_models(source_data):
    extracted_data = []
    for category in source_data:
        if "dataModels" in category and category["dataModels"]:
            extracted_data.extend(category["dataModels"])
    return extracted_data

# 获取并存储搜索数据
def sql_data_searchdata():
    # 接口配置
    custom_url = "https://www.aijx3.cn/api2/aijx3-wblwg/basedata/getSearchData"
    params = {}
    
    try:
        # 获取数据
        source_data = api_data_post(custom_url, params, "data")
        if not source_data:
            return "获取数据失败或数据为空"
        
        # 处理数据
        extracted_data = extract_data_models(source_data)
        if not extracted_data:  # 修正：应该是extracted_data而不是source_data
            return "未提取到数据"
        
        # 连接数据库并插入数据
        with pymysql.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                # 清空表数据        
                cursor.execute("TRUNCATE TABLE searchdata")
                
                # 准备SQL和批量数据
                sql = """
                INSERT INTO searchdata 
                (typeName, name, showName, picUrl, searchId, searchDescType) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                # 使用列表推导式简化数据准备
                values_list = [
                    (
                        item['typeName'],
                        item['name'],
                        item['showName'],
                        item['picUrl'],
                        item['searchId'],
                        item['searchDescType']
                    )
                    for item in extracted_data
                ]
                
                # 批量插入
                cursor.executemany(sql, values_list)
                connection.commit()
                
                return f"成功批量插入 {len(extracted_data)} 条数据！"
       
    except pymysql.Error as e:
        return f"数据库操作失败: {e}"
    except Exception as e:
        return f"操作失败: {e}"

# 根据搜索字符串查询匹配的数据
def sql_data_select(search_string):
    """
    根据搜索字符串查询匹配的数据
    
    Args:
        search_string: 搜索字符串
        
    Returns:
        匹配的第一条记录，如果没有匹配则返回None
    """
    try:
        with pymysql.connect(**db_config) as connection:
            with connection.cursor() as cursor:               
                sql = """
                SELECT searchId, showName, name
                FROM searchdata 
                WHERE name = %s OR showName = %s
                LIMIT 1
                """
                params = (search_string, search_string)

                cursor.execute(sql, params)
                return cursor.fetchone()
                
    except Exception as e:
        logger.error(f"查询数据时出错: {e}")
        return None