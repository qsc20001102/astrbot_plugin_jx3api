from datetime import datetime
import base64
from astrbot.api import logger

from .APIClient import APIClient
from .AsyncMySQL import AsyncMySQL
from .function_basic import load_template,extract_field,flatten_field,extract_fields,gold_to_string,plot_line_chart_base64

class WZRYFunction:
    def __init__(self, api_config,db: AsyncMySQL ):
        self.__api = APIClient()
        self.__db = db
        self.__api_config = api_config

    async def _SELECT_ID(self,name: str):
        """
        查询ID
        """
        sql = "SELECT id FROM wzydid WHERE name = %s or id = %s"
        sqlid = await self.__db.fetch_one(sql, (name,name)) 
        return sqlid["id"] if sqlid else None
    
    async def all_user(self):
        """
        查询所有用户
        """
        sql = "SELECT id,name FROM wzydid"
        sqlid = await self.__db.fetch_all(sql) 
        return_data = "营地ID\t\t昵称\n"
        for m in sqlid:
            return_data += f"{m['id']}\t{m['name']}\n"
        return return_data

    async def add_user(self,id: str ,name: str):
        """
        添加用户
        """
        self_id = await self._SELECT_ID(id)
        if self_id is not None:
            return "该用户已存在，无需重复添加"
        sql = "INSERT INTO wzydid (id,name) VALUES (%s, %s)"
        rowcount = await self.__db.execute(sql, (id,name))  
        if rowcount > 0:
            return f"id:{id}昵称:{name}\n添加成功"
        else:
            return f"id:{id}昵称:{name}\n添加失败，请稍后再试"

    async def update_user(self,id: str ,name: str):
        """
        更新用户
        """
        self_id = await self._SELECT_ID(id)
        if self_id is None:
            return "该用户不存在，请先添加用户"
        sql = "UPDATE wzydid SET name = %s WHERE id = %s"
        rowcount = await self.__db.execute(sql, (name,id))  
        if rowcount > 0:
            return f"id:{id}昵称:{name}\n更新成功"
        else:
            return f"id:{id}昵称:{name}\n更新失败，请稍后再试"

    async def delete_user(self,id: str ):
        """
        删除用户
        """
        self_id = await self._SELECT_ID(id)
        if self_id is None:
            return "该用户不存在，无需删除"
        sql = "DELETE FROM wzydid WHERE id = %s"
        rowcount = await self.__db.execute(sql, (id,))  
        if rowcount > 0:
            return f"id:{id}\n删除成功"
        else:
            return f"id:{id}\n删除失败，请稍后再试"

    async def zhanji(self,name: str ,option: str):
        """
        战绩查询
        """
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["wzry_zhanji"]
        # ID查询
        sql_id = await self._SELECT_ID(name)
        if sql_id is None:
            return_data["msg"] = "未查询到该用户，请确认输入正确的昵称或营地ID"
            return  return_data
        #更新参数
        api_config["params"]["id"] = sql_id
        api_config["params"]["option"] = option
        # 需要提取的字段
        fields = ["gametime","killcnt","deadcnt","assistcnt","gameresult","mvpcnt","losemvp","mapName",
                  "oldMasterMatchScore","newMasterMatchScore","usedTime","winNum","failNum","roleJobName","stars","desc",
                  "gradeGame","heroIcon","godLikeCnt", "firstBlood","hero1TripleKillCnt","hero1UltraKillCnt","hero1RampageCnt","evaluateUrlV3","mvpUrlV3"]
        # 处理返回数据
        try:
            # 获取数据
            data = await self.__api.get(api_config["url"],api_config["params"],"data")        
            if not data:
                return_data["msg"] = "获取接口信息失败"
                return  return_data   
            # 提取字段
            result = extract_fields(data["list"], fields)
            result = result[:25]
            # 数据处理
            for m in result:
                minutes = m["usedTime"] // 60
                seconds = m["usedTime"] % 60
                m["time_str"] = f"{minutes}:{seconds:02d}"
                
            return_data["data"] = result  
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        # 加载模板
        try:
            return_data["temp"] = load_template("wangzhezhanji.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data   
        return_data["code"] = 200       
        return return_data

    async def ziliao(self, name: str):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        # 查询 ID
        sql_id = await self._SELECT_ID(name)
        
        if sql_id is None:
            return_data["msg"] = "未查询到该用户，请确认输入正确的昵称或营地ID"
            return return_data
        api_config = self.__api_config["wzry_ziliao"]
        api_config["params"]["id"] = sql_id

        try:
            data = await self.__api.get(api_config["url"], api_config["params"])
            # 转 base64
            return_data["data"]["img_base64"] = base64.b64encode(data).decode("utf-8")
            return_data["code"] = 200

        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"

        # 加载模板
        try:
            return_data["temp"] = load_template("wzry_zl.html")
        except FileNotFoundError:
            logger.error(f"加载模板失败")
            return_data["msg"] = "系统错误：模板文件不存在"

        return return_data

