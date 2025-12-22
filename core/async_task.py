import asyncio
from pathlib import Path
import json
from typing import Callable, Awaitable, Optional


from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .jx3_service import JX3Service

class AsyncTask:
    """
    异步后台任务类（asyncio版）
    - 支持后台异步循环执行
    - 支持 start/stop
    - 支持设定间隔
    """

    def __init__(self, context: Context, config: AstrBotConfig, jx3fun: JX3Service):
        """
        Args:
            coro: 异步任务函数
            interval: 每次执行间隔（秒）
            auto_start: 是否自动启动
        """
        self.context = context
        self.conf = config
        self.jx3fun = jx3fun
        self.file_path = StarTools.get_data_dir("astrbot_plugin_jx3") / "local_async.json"
        self._file_lock = asyncio.Lock()
        logger.info(f"获取后台数据缓存文件路径成功：{self.file_path}")


    async def set_local_data(self, key: str, value):
        """异步安全写入本地 JSON"""
        async with self._file_lock:
            try:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)

                if not self.file_path.exists():
                    local_data = {}
                else:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        local_data = json.load(f)

                local_data[key] = value

                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(local_data, f, ensure_ascii=False, indent=4)

                logger.debug(f"后台数据写入完成: {key}--{value}")

            except Exception as e:
                logger.error(f"数据写入文件失败：{e}")


    async def get_local_data(self, key: str, default=None):
        """异步安全读取本地 JSON"""
        async with self._file_lock:
            try:
                if not self.file_path.exists():
                    return default

                with open(self.file_path, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)

                value = local_data.get(key, default)
                logger.debug(f"读取数据成功: {key}--{value}")
                return value

            except Exception as e:
                logger.error(f"读取数据文件失败：{e}")
                return default


    async def cycle_kfjk(self):
        """开服监控后台程序"""
        # 获取配置信息
        conf = self.conf.get("kfjk", {})
        self.kfjk_conf = {
            "enable": conf.get("enable", True),
            "time": conf.get("time", 10),
            "umos": conf.get("umos", []),
        }
        # 状态记录
        self.kfjk = {
            "state": False,
            "state_new": False
        }
        try:
            self.kfjk["state"] = await self.get_local_data("kfjk")    # 上一次查询的状态
        except Exception as e:
            logger.error(f"获取本地缓存数据失败: {e}")

        if self.kfjk_conf["enable"]:
            logger.info(f"开服监控功能开启")
        else:
            logger.info(f"开服监控功能关闭")
            return
        
        while self.kfjk_conf["enable"]:
            try:
                # 获取最新服务状态
                data = await self.jx3fun.kaifu("梦江南")
                self.kfjk["state_new"] = data["status"]
                logger.debug(f"开服监控功能循环中,上次询问服务器状态{self.kfjk['state']},本次询问的服务器状态{self.kfjk['state_new']}") 
                # 判断状态是否变化
                if self.kfjk["state"] != self.kfjk["state_new"]:
                    logger.info(f"开服监控功能循环中,上次询问服务器状态{self.kfjk['state']},本次询问的服务器状态{self.kfjk['state_new']}") 
                    # 构建不同的推送小时
                    message_chain = MessageChain().message(data.get("data"))
                    # 推送消息
                    if self.kfjk_conf["umos"]:
                        for umo in self.kfjk_conf["umos"]:
                            await self.context.send_message(umo, message_chain)

                    await self.set_local_data("kfjk", self.kfjk["state_new"])

                self.kfjk["state"] = self.kfjk["state_new"]
                
            except Exception as e:
                logger.error(f"开服监控循环异常: {e}")
            await asyncio.sleep(self.kfjk_conf["time"])  


    async def get_kfjk_conf(self) -> str:
        """获取开服监控配置信息"""
        return_msg =  f"开服监控后台状态：{self.kfjk_conf['enable']}\n"
        return_msg += f"周期询问时间：{self.kfjk_conf['time']}秒\n"
        return_msg += f"上次询问服务器状态{self.kfjk['state']}\n"
        return_msg += f"本次询问的服务器状态{self.kfjk['state_new']}\n"
        return_msg += f"推送会话列表：\n{self.kfjk_conf['umos']}"
        return return_msg
    

    async def cycle_xwzx(self):
        """最新新闻资讯后台程序"""
        # 获取配置信息
        conf = self.conf.get("xwzx", {})
        self.xwzx_conf = {
            "enable": conf.get("enable", True),
            "time": conf.get("time", 280),
            "umos": conf.get("umos", []),
        }
        # 状态记录
        self.xwzx = {
            "state": 0,
            "state_new": 0
        }

        try:
            self.xwzx["state"] = await self.get_local_data("xwzx")    # 上一次查询的状态
        except Exception as e:
            logger.error(f"获取本地缓存数据失败: {e}")

        if self.xwzx_conf["enable"]:
            logger.info(f"新闻资讯推送功能开启")
        else:
            logger.info(f"新闻资讯推送功能关闭")
            return
        
        while self.xwzx_conf["enable"]:
            try:
                # 获取最新服务状态
                data = await self.jx3fun.xinwei()
                self.xwzx["state_new"] = data["status"]
                logger.debug(f"新闻资讯推送功能循环中,上次最新资讯ID{self.xwzx['state']},本次最新资讯ID{self.xwzx['state_new']}") 
                # 判断状态是否变化
                if self.xwzx["state"] != self.xwzx["state_new"]:
                    logger.info(f"新闻资讯推送功能循环中,上次最新资讯ID{self.xwzx['state']},本次最新资讯ID{self.xwzx['state_new']}") 
                    # 构建不同的推送小时
                    message_chain = MessageChain().message(data.get("data"))
                    # 推送消息
                    if self.xwzx_conf["umos"]:
                        for umo in self.xwzx_conf["umos"]:
                            await self.context.send_message(umo, message_chain)

                    await self.set_local_data("xwzx", self.xwzx["state_new"])

                self.xwzx["state"] = self.xwzx["state_new"]
                
            except Exception as e:
                logger.error(f"开服监控循环异常: {e}")
            await asyncio.sleep(self.xwzx_conf["time"])  