from datetime import datetime

from astrbot.api import logger

from .api_data import APIClient
from .load_template import load_template

class JX3Function:
    def __init__(self, api_config):
        self.__api = APIClient()
        self.__api_config = api_config

    async def richang(self,server: str = "眉间雪",num: int = 0):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3_richang"]
        #更新参数
        api_config["params"]["server"] = server
        api_config["params"]["num"] = num
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")        
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data      
        # 处理返回数据
        try:
            result_msg = f"{server}-{data.get('date')}-星期{data.get('week')}\n"
            result_msg += f"大战：{data.get('war')}\n"
            result_msg += f"战场：{data.get('battle')}\n"
            result_msg += f"阵营：{data.get('orecar')}\n"
            result_msg += f"宗门：{data.get('school')}\n"
            result_msg += f"驰援：{data.get('rescue')}\n"
            result_msg += f"画像：{data.get('draw')}\n"
            result_msg += f"宠物福缘：\n{data.get('luck')}\n"
            result_msg += f"家园声望：\n{data.get('card')}\n"
            result_msg += f"武林通鉴：\n{data.get('team')}\n"
            return_data["data"] = result_msg
            return_data["code"] = 200       
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data


    async def shapan(self,server: str = "眉间雪"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_shapan"]
        #更新参数
        api_config["params"]["serverName"] = server
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")         
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data        
        # 处理返回数据
        try:
            return_data["data"] = data.get("picUrl")
            return_data["code"] = 200       
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data


    async def shaohua(self):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3_shaohua"]
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")         
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data        
        # 处理返回数据
        try:
            return_data["data"] = data.get("text")
            return_data["code"] = 200       
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data


    async def jigai(self):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3_jigai"]
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")         
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data 
        # 处理返回数据
        try:
            result_msg = f"剑网三最近技改\n"
            for i, item in enumerate(data[:2], 1):
                result_msg += f"{i}. {item.get('title', '无标题')}\n"
                result_msg += f"时间：{item.get('time', '未知时间')}\n"
                result_msg += f"链接：{item.get('url', '无链接')}\n\n"
            return_data["data"] = result_msg
            return_data["code"] = 200          
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data
    

    async def jinjia(self, server: str = "眉间雪"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_jinjia"]
        #更新参数
        api_config["params"]["serverName"] = server
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data 
        # 加载模板
        try:
            return_data["temp"] = load_template("jinjia.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data
        # 准备模板渲染数据
        try:
            return_data["data"] = {
                "items": data,
                "server": api_config["params"]["serverName"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            } 
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "系统错误：模板渲染数据准备失败"
            return return_data      
        return_data["code"] = 200       
        return return_data


    async def qiyu(self, adventureName: str = "阴阳两界", serverName: str = "眉间雪"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_qiyu"]
        #更新参数
        api_config["params"]["adventureName"] = adventureName
        api_config["params"]["serverName"] = serverName
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data
        # 格式化时间
        for item in data:
            if "time" in item:
                item["time"] = datetime.fromtimestamp(item["time"]/1000).strftime("%Y-%m-%d %H:%M:%S")
        # 加载模板
        try:
            return_data["temp"] = load_template("qiyuliebiao.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data
        # 准备模板渲染数据
        try:            
            return_data["data"] = {
                "items": data,
                "server": serverName,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ,"qiyuname": adventureName
            }
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "系统错误：模板渲染数据准备失败"
            return return_data      
        return_data["code"] = 200       
        return return_data