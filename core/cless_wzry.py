from datetime import datetime
import base64
from astrbot.api import logger

from .class_reqsest import APIClient
from .cless_mysql import AsyncMySQL
from .function_basic import load_template,extract_field,flatten_field,extract_fields,gold_to_string,plot_line_chart_base64

class WZRYFunction:
    def __init__(self, api_config,db: AsyncMySQL ):
        self.__api = APIClient()
        self.__db = db
        self.__api_config = api_config

    async def zhanji(self,id: str ,option: str):
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
        #更新参数
        api_config["params"]["id"] = id
        api_config["params"]["option"] = option
        fields = ["gametime","killcnt","deadcnt","assistcnt","gameresult","mvpcnt","losemvp","mapName",
                  "oldMasterMatchScore","newMasterMatchScore","usedTime","winNum","failNum","roleJobName","stars","desc",
                  "gradeGame","heroIcon"]
        # 处理返回数据
        try:
            # 获取数据
            data = await self.__api.get(api_config["url"],api_config["params"],"data")        
            if not data:
                return_data["msg"] = "获取接口信息失败"
                return  return_data   
            result = extract_fields(data["list"], fields)
            result = result[:15]
            # 数据处理
            for m in result:
                minutes = m["usedTime"] // 60
                seconds = m["usedTime"] % 60
                m["time_str"] = f"{minutes}:{seconds:02d}"
                    # 可选：提前转义 gameresult
                if m["gameresult"] == 1:
                    m["gameresult_label"] = "胜利"
                    m["gameresult_bg"] = "#e6fbf1"
                    m["gameresult_color"] = "#056a3a"
                elif m["gameresult"] == 2:
                    m["gameresult_label"] = "失败"
                    m["gameresult_bg"] = "#fff0f0"
                    m["gameresult_color"] = "#9c1f1f"
                else:
                    m["gameresult_label"] = "平局"
                    m["gameresult_bg"] = "#eee"
                    m["gameresult_color"] = "#555"
                m["MVP"] = "混子"
                if m["mvpcnt"] ==1:
                    m["MVP"] = "胜方MVP"
                if m["mvpcnt"] ==1:
                    m["MVP"] = "败方MVP"
                
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

    async def ziliao(self,id: str):
        """
        资料查询
        """
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["wzry_ziliao"]
        #更新参数
        api_config["params"]["id"] = id
        # 处理返回数据
        try:
            # 获取数据
            data = await self.__api.get(api_config["url"],api_config["params"])        
            if not data:
                return_data["msg"] = "获取接口信息失败"
                return  return_data   
            # 数据处理
            return_data["data"]["img_base64"] = base64.b64encode(data).decode('utf-8')
               
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        # 加载模板
        try:
            return_data["temp"] = load_template("temp_test.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data   
        return_data["code"] = 200       
        return return_data
