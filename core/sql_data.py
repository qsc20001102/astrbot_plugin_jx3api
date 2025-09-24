import pymysql
import time
from astrbot.api import logger
from .api_data import api_data_get, api_data_post


# 提取所有 dataModels 中的数据
def extract_data_models(source_data):
    extracted_data = []
    for category in source_data:
        if "dataModels" in category and category["dataModels"]:
            extracted_data.extend(category["dataModels"])
    return extracted_data


def sql_data_searchdata():

    # 接口URL
    custom_url = "https://www.aijx3.cn/api2/aijx3-wblwg/basedata/getSearchData"  
    # 接口参数
    params = {

    }

    # 连接数据库
    connection = pymysql.connect(
        host='45.205.31.132',      # 数据库主机地址
        port=5211,                 # 数据库端口
        user='asrtbot',  # 数据库用户名
        password='qsc123456',  # 数据库密码
        database='asrtbot',  # 数据库名
        charset='utf8mb4'      # 字符编码
        )
    
    # 获取数据
    try:
        source_data = api_data_post(custom_url,params,"data")

        if not source_data:
            test = "获取数据失败或数据为空"
            return
        
    except Exception as e:
        test = f"获取数据时出错: {e}"

    #处理数据
    extracted_data = extract_data_models(source_data)
    if not source_data:
        test = "未提取到数据"
        return
    
    # 插入数据到数据库
    try:
        with connection.cursor() as cursor:
            # 清空表数据        
            cursor.execute("TRUNCATE TABLE searchdata")

            # 准备 SQL 插入语句
            sql = """
            INSERT INTO searchdata 
            (typeName, name, showName, picUrl, searchId, searchDescType) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
 
            # 准备批量数据
            values_list = []
            for item in extracted_data:
                values_list.append((
                    item['typeName'],
                    item['name'],
                    item['showName'],
                    item['picUrl'],
                    item['searchId'],
                    item['searchDescType']
                ))
                
            # 批量插入
            cursor.executemany(sql, values_list)
            connection.commit()
            test = f"成功批量插入 {len(extracted_data)} 条数据！"

    except Exception as e:
        test = f"插入数据时出错: {e}"
        connection.rollback()

    finally:
        connection.close()

    return test


def sql_data_select(search_string):

    # 连接数据库
    connection = pymysql.connect(
        host='45.205.31.132',      # 数据库主机地址
        port=5211,                 # 数据库端口
        user='asrtbot',  # 数据库用户名
        password='qsc123456',  # 数据库密码
        database='asrtbot',  # 数据库名
        charset='utf8mb4'      # 字符编码
        )

    results = []

    # 插入数据到数据库
    try:
        with connection.cursor() as cursor:
            # 准备 SQL 插入语句
            sql = """
            SELECT searchId, showName 
            FROM searchdata 
            WHERE name = %s OR showName = %s
            """
 
            # 添加通配符 % 到搜索字符串的两端
            #search_pattern = f"%{search_string}%"

            # 执行查询
            cursor.execute(sql, (search_string, search_string))

            # 获取所有匹配的结果
            rows = cursor.fetchall()

            # 将结果转换为字典列表
            for row in rows:
                results.append({
                    "searchId": row[0],
                    "showName": row[1]
                })

    except Exception as e:
        logger.error(f"查询数据时出错: {e}")

    finally:
        connection.close()

    return results[0] 