import urllib3
from datetime import datetime
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .core.load_template import load_template
from .core.jx3_data import jx3_data_jiaoyihang,jx3_data_wujia
from .core.api_data import api_data_get, api_data_post
from .core.sql_data import sql_data_searchdata,sql_data_select

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
        """剑三日常"""
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
        data = api_data_get(custom_url, params,"data")
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 处理返回数据
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


    @filter.command("剑三骚话")
    async def jx3_shaohua(self, event: AstrMessageEvent):
        """剑三骚话"""
        # 接口URL
        custom_url = "https://www.jx3api.com/data/saohua/random"  
        # 接口参数
        params = {
            "name": "万花",  # 默认值
        }
        
        # 获取消息内容

        # 解析消息内容
        
        # 获取数据
        data = api_data_get(custom_url, params,"data")
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 处理返回数据
        try:
            # 构建回复消息
            result_msg = f"{data.get('text')}\n"

            yield event.plain_result(result_msg)
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错")


    @filter.command("剑三技改")
    async def jx3_jigai(self, event: AstrMessageEvent):
        """剑三技改"""
        # 接口URL
        custom_url = "https://www.jx3api.com/data/skills/records"  
        # 接口参数
        params = {
            
        }
        
        # 获取消息内容

        # 解析消息内容
        
        # 获取数据
        data = api_data_get(custom_url,params,"data")
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 处理返回数据
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


    @filter.command("剑三交易行")
    async def jx3_data_jiaoyihang(self, event: AstrMessageEvent):
        """剑三交易行 物品名称 服务器""" 

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
            params["name"] = parts[1]  

        if len(parts) > 2:
            params["server"] = parts[2]  

        # 获取交易行数据
        try:
            items_data = jx3_data_jiaoyihang(params["server"], params["name"])

            if not items_data or items_data == "无交易行数据":
                yield event.plain_result(f"在服务器【{params['server']}】未找到物品【{params['name']}】的交易行数据")      
                return

            if not items_data or items_data == "未找到改物品":
                yield event.plain_result(f"未找到物品【{params['name']}】")      
                return

            # 加载模板
            try:
                template_content = load_template("jiaoyihang.html")
            except FileNotFoundError as e:
                logger.error(f"加载模板失败: {e}")
                yield event.plain_result("系统错误：模板文件不存在")
                return
                
            # 准备模板渲染数据
            render_data = {
                "items": items_data,
                "server": params["server"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }      

            url = await self.html_render(template_content, render_data, options={})
            yield event.image_result(url)
        
        except Exception as e:
            logger.error(f"交易行查询出错: {e}")
            yield event.plain_result("查询交易行数据时出错，请稍后再试")


    @filter.command("剑三沙盘")
    async def jx3_shapan(self, event: AstrMessageEvent):
        """剑三沙盘 服务器"""
        # 接口URL
        custom_url = "https://www.jianxiachaguan.cn/api2/aijx3-jxcg/game/get-sand-table-img"  
        # 接口参数
        params = {
                "serverName": "眉间雪"  # 默认服务器
        }

        # 获取消息内容
        message_str = event.message_str.strip()
        parts = message_str.split()
        # 解析消息内容
        if len(parts) > 1:
            params["serverName"] = parts[1]  # 第二个参数为服务器

        # 获取数据
        data = api_data_post(custom_url,params,"data")
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 处理返回数据
        try:
            # 构建回复消息
            yield event.image_result(data.get("picUrl"))
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错")


    @filter.command("剑三金价")
    async def jx3_jinjia(self, event: AstrMessageEvent):
        """剑三金价 服务器"""
        # 接口URL
        custom_url = "https://www.jianxiachaguan.cn/api2/aijx3-jxcg/game/get-gold"  
        # 接口参数
        params = {
                "serverName": "眉间雪"  # 默认服务器
        }

        # 获取消息内容
        message_str = event.message_str.strip()
        parts = message_str.split()
        # 解析消息内容
        if len(parts) > 1:
            params["serverName"] = parts[1]  # 服务器

        # 获取数据
        data = api_data_post(custom_url,params,"data")
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        # 处理返回数据
        try:
            # 加载模板
            try:
                template_content = load_template("jinjia.html")
            except FileNotFoundError as e:
                logger.error(f"加载模板失败: {e}")
                yield event.plain_result("系统错误：模板文件不存在")
                return
            # 准备模板渲染数据
            render_data = {
                "items": data,
                "server": params["serverName"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            } 

            url = await self.html_render(template_content, render_data, options={})
            yield event.image_result(url)

        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错")


    @filter.command("剑三奇遇")
    async def jx3_qiyu(self, event: AstrMessageEvent):
        """剑三奇遇 奇遇名称 服务器"""
        # 接口URL
        custom_url = "https://www.jianxiachaguan.cn/api2/aijx3-jxcg/game/get-adventure-record"  
        # 接口参数
        params = {
            "adventureName": "阴阳两界",  # 默奇遇
            "serverName": "眉间雪"  # 默认服务器
        }

        # 获取消息内容
        message_str = event.message_str.strip()
        parts = message_str.split()
        # 解析消息内容
        if len(parts) > 1:
            params["adventureName"] = parts[1]  # 奇遇名称
        if len(parts) > 2:
            params["serverName"] = parts[2]  # 第二个参数为服务器

        # 获取数据
        data = api_data_post(custom_url,params,"data")
        
        if not data:
            yield event.plain_result("获取获取接口信息失败，请稍后再试")
            return
        
        #数据处理
        for item in data:
            # 格式化时间
            if "time" in item:
                dt = datetime.fromtimestamp(item["time"]/1000)
                item["time"] = dt.strftime("%Y-%m-%d %H:%M:%S")

        # 传入模板渲染
        try:
            # 加载模板
            try:
                template_content = load_template("qiyuliebiao.html")
            except FileNotFoundError as e:
                logger.error(f"加载模板失败: {e}")
                yield event.plain_result("系统错误：模板文件不存在")
                return
            # 准备模板渲染数据
            render_data = {
                "items": data,
                "server": params["serverName"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ,"qiyuname": params["adventureName"]
            }

            url = await self.html_render(template_content, render_data, options={})
            yield event.image_result(url)
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错") 


    @filter.command("剑三外观数据同步")
    async def jx3_SearchData(self, event: AstrMessageEvent):
        """剑三外观数据同步"""
     
        try:
            test = sql_data_searchdata()
            yield event.plain_result(f"{test}") 
            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错") 


    @filter.command("剑三物价")
    async def jx3_wujia(self, event: AstrMessageEvent):
        """剑三物价 外观名称"""

        inname = "秃盒"

        # 获取消息内容
        message_str = event.message_str.strip()
        parts = message_str.split()
        # 解析消息内容
        if len(parts) > 1:
            inname = parts[1]  # 外观名称

        try:      
            # 加载模板
            try:
                template_content = load_template("wujia.html")
            except FileNotFoundError as e:
                logger.error(f"加载模板失败: {e}")
                yield event.plain_result("系统错误：模板文件不存在")
                return

            render_data = jx3_data_wujia(inname)

            if render_data.get("code") == "200":
                url = await self.html_render(template_content, render_data, options={})
                yield event.image_result(url)
            else:
                yield event.plain_result(f"{render_data.get('msg')}")
                return
            

            
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            yield event.plain_result("处理接口返回信息时出错") 


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""