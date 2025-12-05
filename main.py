import json
import shutil
import asyncio
import pathlib
from pathlib import Path
from typing import Union
from datetime import datetime

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .core.aiosqlite import AsyncSQLite
from .core.jx3_service import JX3Service
from .core.async_task import AsyncTask


@register("astrbot_plugin_jx3", 
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
        local_data_dir = StarTools.get_data_dir("astrbot_plugin_jx3")
        # 插件数据文件路径
        data_file_path = Path(__file__).parent / "data"
        # --- 调用函数完成检查和复制 ---
        try:
            self.file_local_data = self.check_and_copy_db(
                local_data_dir=local_data_dir,
                db_filename="local_data.db",
                default_db_dir=data_file_path
            )
        except FileNotFoundError as e:
            # 处理默认文件丢失的严重错误
            logger.critical(f"插件初始化失败：{e}")
            raise # 中断初始化
        # 读取API配置文件
        self.api_file_path = Path(__file__).parent / "data" / "api_config.json"
        with open(self.api_file_path, 'r', encoding='utf-8') as f:
            self.api_config = json.load(f)  
        # 初始化数据
        #self.kf_task = asyncio.create_task(self.cycle_kaifjiankong()) 
        logger.info("jx3api插件初始化完成")


    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""     
        #创建类实例
        self.db = AsyncSQLite(str(self.file_local_data))
        self.jx3fun = JX3Service(self.api_config,self.db)
        self.at = AsyncTask(self.context, self.conf, self.jx3fun)
        # 周期函数调用
        self.kf_task = asyncio.create_task(self.at.cycle_kfjk())


        logger.info("jx3api异步插件初始化完成")


    def check_and_copy_db(self, local_data_dir: Union[str, Path], db_filename: str, default_db_dir: Union[str, Path]) -> pathlib.Path:
        """
        检查本地数据目录中是否存在指定的数据库文件。
        如果不存在，则从默认目录复制该文件。
        Args:
            local_data_dir: 目标数据库文件所在的文件夹路径。
            db_filename: 数据库文件的名称 (例如: 'local_data.db')。
            default_db_dir: 默认/源数据库文件所在的文件夹路径。
        Returns:
            最终的数据库文件的完整 pathlib.Path 对象。
        Raises:
            FileNotFoundError: 如果默认的源数据库文件不存在。
        """
        # 目标路径
        target_dir = pathlib.Path(local_data_dir)
        target_file_path = target_dir / db_filename
        # 源文件路径
        source_file_path = pathlib.Path(default_db_dir) / db_filename
        # 假设默认文件名为 local_data.db
        if not target_file_path.exists():
            logger.warning(f"本地数据库文件 {target_file_path.name} 不存在，正在从默认位置复制...")
            # 1. 确保目标文件夹存在
            target_dir.mkdir(parents=True, exist_ok=True)
            # 2. 检查源文件是否存在
            if not source_file_path.exists():
                raise FileNotFoundError(f"默认数据库源文件未找到！请检查路径: {source_file_path}")
            # 3. 复制文件
            shutil.copy(source_file_path, target_file_path)
            logger.info(f"数据库文件已成功复制到: {target_file_path}")
        else:
            logger.info(f"本地数据库文件 {target_file_path} 已存在，跳过复制。")
        return target_file_path

    
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
                yield event.plain_result(data["msg"])
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
                yield event.plain_result(data["msg"])
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
    async def jx3_kaifhujiank(self, event: AstrMessageEvent):
        """剑三 开服监控"""     
        return_msg = await self.at.get_kfjk_conf()
        yield event.plain_result(return_msg) 



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
        # 关闭数据库连接
        await self.db.close()
        # 后台z周期进程销毁
        self.kf_task.cancel()
        logger.info("jx3api插件已卸载/停用")