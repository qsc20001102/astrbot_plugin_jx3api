import json
import asyncio
from pathlib import Path
from datetime import datetime

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .core.async_mysql import AsyncMySQL
from .core.jx3_service import JX3Service



@register("剑网三数据查询工具", 
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
        # 初始化数据
        self.inidata()
        self.kf_task = asyncio.create_task(self.cycle_kaifjiankong()) 
        logger.info("jx3api插件初始化完成")


    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        # 数据库配置
        db_config = {
            'host': '38.12.28.24',
            'port': 3306,
            'user': 'asrtbot',
            'password': 'qsc123456',
            'db': 'asrtbot',  
            'charset': 'utf8mb4',
            'autocommit': True
        }        
        #创建类实例
        self.db = AsyncMySQL(db_config)
        self.jx3fun = JX3Service(self.api_config,self.db)
        # 周期函数调用
    

        logger.info("jx3api插件创建实例完成")

    def inidata(self):
        """数据初始化"""
        self.test_server = False
        logger.info("数据初始化完成")


    async def cycle_kaifjiankong(self):
        """开服监控后台程序"""
        # 获取配置信息
        time_int = self.conf.get("jx3_kfjk_time", 10)
        self.kfjk_en = self.conf.get("jx3_kfjk_en", True)
        self.kfjk_umos = self.conf.get("jx3_kfjk_list", [])
        self.kfjk_servername = self.conf.get("jx3_kfjk_server", "梦江南")
        kfjk_test = self.conf.get("jx3_kfjk_test", False)

        self.kfjk_server_state = True    # 上一次查询的状态
        self.kfjk_server_state_new = False  # 最新查询的状态

        if self.kfjk_en:
            logger.info(f"开服监控功能开启")
        while self.kfjk_en:
            data = await self.jx3fun.kaifu(self.kfjk_servername)
            if kfjk_test:
                self.kfjk_server_state_new = self.test_server
            else:
                self.kfjk_server_state_new = data["status"]
            # logger.info(f"开服监控功能循环中,上次询问服务器状态{self.kfjk_server_state},本次询问的服务器状态{self.kfjk_server_state_new}") 
            if self.kfjk_server_state != self.kfjk_server_state_new:
                logger.info(f"开服监控功能循环中,上次询问服务器状态{self.kfjk_server_state},本次询问的服务器状态{self.kfjk_server_state_new}") 
                if self.kfjk_server_state and not self.kfjk_server_state_new:
                    message_chain = MessageChain().message(f"{self.kfjk_servername}服务器已关闭\n休息一会把,开服了喊你！")
                if self.kfjk_server_state_new and not self.kfjk_server_state:
                    message_chain = MessageChain().message(f"{self.kfjk_servername}服务器已开启\n快冲！快冲！")
                if self.kfjk_umos:
                    for umo in self.kfjk_umos:
                        await self.context.send_message(umo, message_chain)
            self.kfjk_server_state = self.kfjk_server_state_new
            await asyncio.sleep(time_int)
        if not self.kfjk_en: 
            # 销毁进程
            self.kf_task.cancel()
            logger.info(f"开服监控功能关闭")
    

    @filter.command_group("剑三")
    def jx3(self):
        pass


    @jx3.command("日常")
    async def jx3_richang(self, event: AstrMessageEvent,server: str = "梦江南",num: int = 0):
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
    

    @jx3.command("开服")
    async def jx3_kaifu(self, event: AstrMessageEvent,server: str = "梦江南"):
        """剑三 日常 服务器 天数"""
        try:
            data= await self.jx3fun.kaifu(server)
            if data["code"] == 200:
                yield event.plain_result(data["data"])
            else:
                yield event.plain_result("msg")
            return
        except Exception as e:
            logger.error(f"功能函数执行错误: {e}")
            yield event.plain_result("猪脑过载，请稍后再试")


    @jx3.command("沙盘")
    async def jx3_shapan(self, event: AstrMessageEvent,server: str = "梦江南"):
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
    async def jx3_jinjia(self, event: AstrMessageEvent,server: str = "梦江南"):
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
    async def jx3_qiyu(self, event: AstrMessageEvent,adventureName: str = "阴阳两界", serverName: str = "梦江南"):
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


    @jx3.command("开服监控")
    async def jx3_kaifhujiank(self, event: AstrMessageEvent,en: str = "状态"):
        """剑三 开服监控"""     
        if en == "开启":
            umo_set = set(self.kfjk_umos)
            umo_set.add(event.unified_msg_origin)
            self.kfjk_umos = list(umo_set)
            yield event.plain_result(f"开服监控已开启") 
        elif en =="关闭":
            try:
                self.kfjk_umos.remove(event.unified_msg_origin)
                yield event.plain_result(f"开服监控已关闭")
            except ValueError as e:
                yield event.plain_result(f"开服监控已关闭") 
        elif en == "状态":
            yield event.plain_result(f"开服监控后台状态：{self.kfjk_en}\n监控服务器：{self.kfjk_servername}\n上次询问服务器状态{self.kfjk_server_state}\n本次询问的服务器状态{self.kfjk_server_state_new}\n推送会话列表：\n{self.kfjk_umos}") 
        else:
            yield event.plain_result("开服监控指令错误，请输入 开启/关闭") 


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


    @filter.command("测试值")
    async def jx3_testvar(self, event: AstrMessageEvent,var: str = "0"):
        """测试程序"""   
        if var == "1":
            self.test_server = True
        if var == "0":
            self.test_server = False
        
        yield event.plain_result(f"测试值:{self.test_server}") 


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        await self.db.close_pool()
        # 后台进程销毁
        self.kf_task.cancel()
        logger.info("jx3api插件已卸载/停用")