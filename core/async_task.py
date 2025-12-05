import asyncio
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


    async def cycle_kaifjiankong(self):
        """开服监控后台程序"""
        # 获取配置信息
        conf = self.conf.get("kfjk", {})
        self.kfjk_conf = {
            "enable": conf.get("enable", True),
            "time": conf.get("time", 10),
            "umos": conf.get("umos", []),
        }

        self.kfjk_server_state = True    # 上一次查询的状态
        self.kfjk_server_state_new = False  # 最新查询的状态

        if self.kfjk_conf["enable"]:
            logger.info(f"开服监控功能开启")
        while self.kfjk_conf["enable"]:
            # 获取最新服务状态
            data = await self.jx3fun.kaifu("梦江南")
            self.kfjk_server_state_new = data["status"]
            # 判断状态是否变化
            if self.kfjk_server_state != self.kfjk_server_state_new:
                logger.info(f"开服监控功能循环中,上次询问服务器状态{self.kfjk_server_state},本次询问的服务器状态{self.kfjk_server_state_new}") 
                if self.kfjk_server_state and not self.kfjk_server_state_new:
                    message_chain = MessageChain().message("剑网三服务器已关闭\n休息一会把,开服了喊你！")
                if self.kfjk_server_state_new and not self.kfjk_server_state:
                    message_chain = MessageChain().message("剑网三服务器已开启\n快冲！快冲！")
                if self.kfjk_conf["umos"]:
                    for umo in self.kfjk_conf["umos"]:
                        await self.context.send_message(umo, message_chain)
            self.kfjk_server_state = self.kfjk_server_state_new
            await asyncio.sleep(self.kfjk_conf["time"])  # 休眠指定时间（分钟）

    async def get_kfjk_conf(self) -> str:
        """获取开服监控配置信息"""
        return_msg =  f"开服监控后台状态：{self.kfjk_conf['enable']}\n"
        return_msg += f"周期询问时间：{self.kfjk_conf['time']}秒\n"
        return_msg += f"上次询问服务器状态{self.kfjk_server_state}\n"
        return_msg += f"本次询问的服务器状态{self.kfjk_server_state_new}\n"
        return_msg += f"推送会话列表：\n{self.kfjk_conf['umos']}"
        return return_msg