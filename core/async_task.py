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

        time_int = self.conf.get("jx3_kfjk_time", 10)
        self.kfjk_en = self.conf.get("jx3_kfjk_en", True)
        self.kfjk_umos = self.conf.get("jx3_kfjk_list", [])
        kfjk_test = self.conf.get("jx3_kfjk_test", False)

        self.kfjk_server_state = True    # 上一次查询的状态
        self.kfjk_server_state_new = False  # 最新查询的状态

        if self.kfjk_en:
            logger.info(f"开服监控功能开启")
        while self.kfjk_en:
            data = await self.jx3fun.kaifu("梦江南")
            if kfjk_test:
                self.kfjk_server_state_new = False
            else:
                self.kfjk_server_state_new = data["status"]
            # logger.info(f"开服监控功能循环中,上次询问服务器状态{self.kfjk_server_state},本次询问的服务器状态{self.kfjk_server_state_new}") 
            if self.kfjk_server_state != self.kfjk_server_state_new:
                logger.info(f"开服监控功能循环中,上次询问服务器状态{self.kfjk_server_state},本次询问的服务器状态{self.kfjk_server_state_new}") 
                if self.kfjk_server_state and not self.kfjk_server_state_new:
                    message_chain = MessageChain().message("剑网三服务器已关闭\n休息一会把,开服了喊你！")
                if self.kfjk_server_state_new and not self.kfjk_server_state:
                    message_chain = MessageChain().message("剑网三服务器已开启\n快冲！快冲！")
                if self.kfjk_umos:
                    for umo in self.kfjk_umos:
                        await self.context.send_message(umo, message_chain)
            self.kfjk_server_state = self.kfjk_server_state_new
            await asyncio.sleep(time_int)
