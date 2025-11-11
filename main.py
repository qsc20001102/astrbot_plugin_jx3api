import json
from pathlib import Path
from datetime import datetime

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .core.cless_mysql import AsyncMySQL
from .core.cless_jx3 import JX3Function


@register("astrbot_plugin_jx3api", 
          "fxdyz", 
          "通过接口调用剑网三API接口获取游戏数据", 
          "1.0.0",
          "https://github.com/qsc20001102/astrbot_plugin_jx3api.git"
)
class Jx3ApiPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        #获取配置
        self.conf = config
        # 本地数据存储路径
        self.local_data_dir = StarTools.get_data_dir("astrbot_plugin_jx3api")
        # api数据文件
        self.api_file_path = Path(__file__).parent / "api_config.json"
        # 读取文件内容
        with open(self.api_file_path, 'r', encoding='utf-8') as f:
            self.api_config = json.load(f)  

        logger.info("jx3api插件初始化完成")


    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        # 数据库配置
        db_config = {
            'host': '154.201.70.116',
            'port': 3306,
            'user': 'asrtbot',
            'password': 'qsc123456',
            'db': 'asrtbot',  
            'charset': 'utf8mb4',
            'autocommit': True
        }        
        #创建类实例
        self.db = AsyncMySQL(db_config)
        self.jx3fun = JX3Function(self.api_config,self.db)
        logger.info("jx3api插件创建实例完成")

         
    
    @filter.command_group("剑三")
    def jx3(self):
        pass

    @jx3.command("日常")
    async def jx3_richang(self, event: AstrMessageEvent,server: str = "眉间雪",num: int = 0):
        """剑三 日常 服务器 天数"""
        try:
            data= await self.jx3fun.richang(server,num)
            if data["code"] == 200:
                yield event.plain_result(data["data"])
            else:
                yield event.plain_result("msg")
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试")
    
    @jx3.command("沙盘")
    async def jx3_shapan(self, event: AstrMessageEvent,server: str = "眉间雪"):
        """剑三 沙盘 服务器"""
        try:
            data= await self.jx3fun.shapan(server)
            if data["code"] == 200:
                yield event.image_result(data["data"])
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试")        


    @jx3.command("骚话")
    async def jx3_shaohua(self, event: AstrMessageEvent,):
        """剑三 骚话"""
        try:
            data= await self.jx3fun.shaohua()
            if data["code"] == 200:
                yield event.plain_result(data["data"])
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 


    @jx3.command("技改")
    async def jx3_jigai(self, event: AstrMessageEvent,):
        """剑三 技改"""
        try:
            data= await self.jx3fun.jigai()
            if data["code"] == 200:
                yield event.plain_result(data["data"])
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 


    @jx3.command("金价")
    async def jx3_jinjia(self, event: AstrMessageEvent,server: str = "眉间雪"):
        """剑三 金价 服务器"""
        try:
            data= await self.jx3fun.jinjia(server)
            if data["code"] == 200:
                url = await self.html_render(data["temp"], data["data"], options={})
                yield event.image_result(url)
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 


    @jx3.command("奇遇")
    async def jx3_qiyu(self, event: AstrMessageEvent,adventureName: str = "阴阳两界", serverName: str = "眉间雪"):
        """剑三 奇遇 奇遇名称 服务器"""
        try:
            data= await self.jx3fun.qiyu(adventureName,serverName)
            if data["code"] == 200:
                url = await self.html_render(data["temp"], data["data"], options={})
                yield event.image_result(url)
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 


    @jx3.command("物价")
    async def jx3_wujia(self, event: AstrMessageEvent,Name: str = "秃盒"):
        """剑三 外观名称"""     
        try:
            data=await self.jx3fun.wujia(Name)
            if data["code"] == 200:
                url = await self.html_render(data["temp"], data["data"], options={})
                yield event.image_result(url)
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 


    @jx3.command("交易行")
    async def jx3_jiaoyihang(self, event: AstrMessageEvent,Name: str = "守缺式",server: str = "梦江南"):
        """剑三 外观名称"""     
        try:
            data=await self.jx3fun.jiaoyihang(Name,server)
            if data["code"] == 200:
                url = await self.html_render(data["temp"], data["data"], options={})
                yield event.image_result(url)
                
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 


    @filter.permission_type(filter.PermissionType.ADMIN)
    @jx3.command("外观数据同步")
    async def jx3_SearchData(self, event: AstrMessageEvent):
        """剑三 外观数据同步"""     
        try:
            data=await self.jx3fun.SearchData()
            if data["code"] == 200:
                yield event.plain_result(data["msg"])
            else:
                yield event.plain_result(data["msg"])
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试") 



    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        await self.db.close_pool()
        logger.info("jx3api插件已卸载/停用")