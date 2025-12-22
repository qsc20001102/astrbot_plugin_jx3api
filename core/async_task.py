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


    async def _cycle_common(self,fetch_func, conf: dict, state: dict, namefun: str, local_key: str):
        """后台程序"""
        # 调用函数获取最新数据
        try:
            state["state_old"] = await self.get_local_data(local_key)
               
        except Exception as e:
            logger.error(f"获取{namefun}本地缓存数据失败: {e}")
        # 判断推送功能是否启用
        if conf["enable"]:
            logger.info(f"{namefun}功能开启")
        else:
            logger.info(f"{namefun}功能关闭")
            return
        # 循环启用
        while conf["enable"]:
            try:
                # 获取最新状态
                data = await fetch_func() 
                state["state_new"] = data["status"]
                logger.debug(f"{namefun}功能循环中,上次询问状态：{state['state_old']},本次询问状态：{state['state_new']}") 
                # 判断状态是否变化
                if state["state_old"] != state["state_new"]:
                    logger.info(f"{namefun}功能循环中,上次询问状态：{state['state_old']},本次询问状态：{state['state_new']}") 
                    # 构建消息
                    message_chain = MessageChain().message(data.get("data"))
                    # 推送消息
                    if conf["umos"]:
                        for umo in conf["umos"]:
                            await self.context.send_message(umo, message_chain)
                    # 状态储存本地
                    await self.set_local_data(local_key, state["state_new"])
                # 最新状态覆盖以前状态
                state["state_old"] = state["state_new"]
                
            except Exception as e:
                logger.error(f"{namefun}循环异常: {e}")
            await asyncio.sleep(conf["time"])  


    async def _get_conf(self, conf: dict, state: dict, namefun: str) -> str:
        """获取功能配置信息"""
        return_msg =  f"{namefun}后台状态：{conf['enable']}\n"
        return_msg += f"周期询问时间：{conf['time']}秒\n"
        return_msg += f"上次询问状态：{state['state_old']}\n"
        return_msg += f"推送会话列表：\n{conf['umos']}"
        return return_msg


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
            "state_old": False,
            "state_new": False
        }

        await self._cycle_common(
            fetch_func=lambda: self.jx3fun.kaifu("梦江南"),
            conf=self.kfjk_conf,
            state=self.kfjk,
            namefun="开服监控",
            local_key="kfjk"
            )


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
            "state_old": 0,
            "state_new": 0
        }
        # 后台进程开启
        await self._cycle_common(
            fetch_func=lambda: self.jx3fun.xinwei(),
            conf=self.xwzx_conf,
            state=self.xwzx,
            namefun="新闻资讯",
            local_key="xwzx"
            )
         

    async def get_kfjk_conf(self) -> str:
        """获取开服监控配置信息"""
        try:
            return_msg = await self._get_conf(self.kfjk_conf, self.kfjk, "开服监控")
        except Exception as e:
            return_msg = f"获取后台配置状态失败：{e}"
        return return_msg
    

    async def get_xwzx_conf(self) -> str:
        """获取开服监控配置信息"""
        try:
            return_msg = await self._get_conf(self.xwzx_conf, self.xwzx, "新闻资讯")
        except Exception as e:
            return_msg = f"获取后台配置状态失败：{e}"
        return return_msg
    