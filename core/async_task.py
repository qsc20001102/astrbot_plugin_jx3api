import asyncio
from pathlib import Path
import json
from typing import Callable, Awaitable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .jx3_service import JX3Service


class AsyncTask:
    """
    基于 APScheduler 的后台异步监控任务管理类
    """

    def __init__(self, context: Context, config: AstrBotConfig, jx3fun: JX3Service):
        self.context = context
        self.conf = config
        self.jx3fun = jx3fun
        
        self.file_path = StarTools.get_data_dir("astrbot_plugin_jx3") / "local_async.json"
        self._file_lock = asyncio.Lock()
        
        self.scheduler = AsyncIOScheduler()
        self.tasks = {}  # 存储 task_id 对应的状态信息
        
        logger.info(f"获取后台数据缓存文件路径成功：{self.file_path}")

    """===================== 本地读写 ====================="""

    async def set_local_data(self, key: str, value):
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

            except Exception as e:
                logger.error(f"数据写入文件失败：{e}")

    async def get_local_data(self, key: str, default=None):
        async with self._file_lock:
            try:
                if not self.file_path.exists():
                    return default
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                return local_data.get(key, default)
            except Exception as e:
                logger.error(f"读取数据文件失败：{e}")
                return default

    """===================== 通用后台任务 ====================="""

    async def _job_common(self, fetch_func, task_key: str, namefun: str):
        state = self.tasks[task_key]
        try:
            data = await fetch_func()
            state["state_new"] = data["status"]

            if state["state_old"] != state["state_new"]:
                message_chain = MessageChain().message(data.get("data"))

                for umo in state["umos"]:
                    await self.context.send_message(umo, message_chain)

                await self.set_local_data(task_key, state["state_new"])
                state["state_old"] = state["state_new"]

        except Exception as e:
            logger.error(f"{namefun}后台任务执行异常: {e}")

    """===================== 初始化任务 ====================="""

    async def init_tasks(self):
        settings = [
            ("kfjk", "开服监控", lambda: self.jx3fun.kaifu("梦江南")),
            ("xwzx", "新闻资讯", lambda: self.jx3fun.xinwei()),
        ]

        for key, name, fetch in settings:
            conf = self.conf.get(key, {})

            state_old = await self.get_local_data(key, default=False)
            self.tasks[key] = {
                "enable": conf.get("enable", True),
                "interval": conf.get("time", 60),
                "umos": conf.get("umos", []),
                "state_old": state_old,
                "state_new": state_old
            }

            if self.tasks[key]["enable"]:
                self._add_scheduler(key, name, fetch)

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("后台监控调度器已启动")

    """===================== 调度操作 ====================="""

    def _add_scheduler(self, key, namefun, fetch_func):
        if self.scheduler.get_job(key):
            self.scheduler.remove_job(key)

        interval = self.tasks[key]["interval"]
        self.scheduler.add_job(
            func=self._job_common,
            trigger=IntervalTrigger(seconds=interval),
            id=key,
            args=[fetch_func, key, namefun]
        )

        logger.info(f"{namefun}后台任务启动成功，周期：{interval}s")

    def stop_all_tasks(self):
        """
        停止并移除所有任务
        """
        try:
            self.scheduler.remove_all_jobs()
            for key in self.tasks:
                self.tasks[key]["enable"] = False
            logger.info("已停止全部后台任务")
        except Exception as e:
            logger.error(f"停止全部后台任务失败：{e}")

    async def destroy(self):
        """
        销毁整个调度器，适合插件卸载/重启时调用
        """
        try:
            self.stop_all_tasks()
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            logger.info("后台调度器已销毁")
        except Exception as e:
            logger.error(f"销毁调度器失败：{e}")

    async def get_task_info(self, key: str) -> str:
        try:
            t = self.tasks[key]
            return (
                f"功能：{key}\n"
                f"启用：{t['enable']}\n"
                f"周期：{t['interval']} 秒\n"
                f"旧状态：{t['state_old']}\n"
                f"推送对象：{t['umos']}"
            )
        except Exception as e:
            return f"读取后台配置失败：{e}"
