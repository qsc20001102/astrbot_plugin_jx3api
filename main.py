import urllib3
from datetime import datetime
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .core.request import fetch_jx3_data
from .core.jx3jiaoyihang import fetch_jx3_jiaoyihang
from .core.load_template import load_template

from jinja2 import Template

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@register("jx3api", "fxdyz", "通过接口调用剑网三API接口获取游戏数据", "1.0.0")
class Jx3ApiPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.conf = config
        print(self.conf)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""


    @filter.command("剑三日常")
    async def jx3_richang(self, event: AstrMessageEvent):
        """获取剑网3日常活动信息"""
        # 接口URL
        custom_url = "https://www.jx3api.com/data/active/calendar"  
        # 接口参数
        params = {
            "server": "眉间雪",  # 默认服务器
            "num": 0  # 默认当天
        }
        
        # 获取消息内容
        message_str = event.message_str.strip()
        parts = message_str.split()

        # 解析消息内容
        if len(parts) > 1:
            params["server"] = parts[1]  # 第二个参数为服务器

        if len(parts) > 2:
            try:
                params["num"] = int(parts[2])  # 第三个参数为日期偏移
            except ValueError:
                params["num"] = 0  # 参数为日期偏移
        # 获取数据
        data = fetch_jx3_data(custom_url, **params)
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 格式化返回消息
        try:
            # 构建回复消息
            result_msg = f"{params['server']}-{data.get('date')}-星期{data.get('week')}\n"
            result_msg += f"大战：{data.get('war')}\n"
            result_msg += f"战场：{data.get('battle')}\n"
            result_msg += f"阵营：{data.get('orecar')}\n"
            result_msg += f"宗门：{data.get('school')}\n"
            result_msg += f"驰援：{data.get('rescue')}\n"
            result_msg += f"画像：{data.get('draw')}\n"
            result_msg += f"宠物福缘：\n{data.get('luck')}\n"
            result_msg += f"家园声望：\n{data.get('card')}\n"
            result_msg += f"武林通鉴：\n{data.get('team')}\n"

            yield event.plain_result(result_msg)
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""


    @filter.command("剑三骚话")
    async def jx3_shaohua(self, event: AstrMessageEvent):
        """随机获取一条与万花门派相关的骚话"""
        # 接口URL
        custom_url = "https://www.jx3api.com/data/saohua/random"  
        # 接口参数
        params = {
            "name": "万花",  # 默认值
        }
        
        # 获取消息内容

        # 解析消息内容
        
        # 获取数据
        data = fetch_jx3_data(custom_url, **params)
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 格式化返回消息
        try:
            # 构建回复消息
            result_msg = f"{data.get('text')}\n"

            yield event.plain_result(result_msg)
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""


    @filter.command("剑三技改")
    async def jx3_jigai(self, event: AstrMessageEvent):
        """查询技能的历史修改记录，包括资料片更新、技能调整等信息"""
        # 接口URL
        custom_url = "https://www.jx3api.com/data/skills/records"  
        # 接口参数
        params = {
            
        }
        
        # 获取消息内容

        # 解析消息内容
        
        # 获取数据
        data = fetch_jx3_data(custom_url,**params)
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 格式化返回消息
        try:
            # 构建回复消息
            result_msg = f"剑网三最近技改\n"
            for i, item in enumerate(data[:2], 1):
                result_msg += f"{i}. {item.get('title', '无标题')}\n"
                result_msg += f"时间：{item.get('time', '未知时间')}\n"
                result_msg += f"链接：{item.get('url', '无链接')}\n\n"

            yield event.plain_result(result_msg)
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""


    @filter.command("剑三交易行")
    async def jx3_jiaoyihang(self, event: AstrMessageEvent):
        """获取剑网3交易行信息""" 

        # 接口参数
        params = {
            "server": "眉间雪",  # 默认服务器
            "name": "守缺"  # 默认当天
        }

        # 获取消息内容
        message_str = event.message_str.strip()
        parts = message_str.split()
        
        # 解析消息内容
        if len(parts) > 1:
            params["server"] = parts[1]  # 第二个参数为服务器

        if len(parts) > 2:
            params["name"] = parts[2]  # 第三个参数为日期偏移

            # 获取交易行数据
        try:
            items_data = fetch_jx3_jiaoyihang(params["server"], params["name"])

            if not items_data or items_data == "无交易行数据":
                yield f"在服务器【{params['server']}】未找到物品【{params['name']}】的交易行数据"
                return
                
            # 加载模板
            try:
                template_content = load_template("jiaoyihang.html")
            except FileNotFoundError as e:
                logger.error(f"加载模板失败: {e}")
                yield "系统错误：模板文件不存在"
                return
                
            # 准备模板渲染数据
            render_data = {
                "items": items_data,
                "server": params["server"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 渲染为图片 - 可能需要调整选项以适应完整HTML文档
            options = {
                "clip": {   
                    "x": 0,
                    "y": 0,
                    "width": 800,
                    "height": 600
                }
            }

            url = await self.html_render(template_content, render_data, options)
            yield event.image_result(url)
        
        except Exception as e:
            logger.error(f"交易行查询出错: {e}")
            yield "查询交易行数据时出错，请稍后再试"

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""

        