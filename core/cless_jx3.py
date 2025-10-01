from datetime import datetime

from astrbot.api import logger

from .class_reqsest import APIClient
from .cless_mysql import AsyncMySQL
from .function_basic import load_template, extract_field,flatten_field,extract_fields,gold_to_string

class JX3Function:
    def __init__(self, api_config,db: AsyncMySQL ):
        self.__api = APIClient()
        self.__db = db
        self.__api_config = api_config

    async def richang(self,server: str = "眉间雪",num: int = 0):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3_richang"]
        #更新参数
        api_config["params"]["server"] = server
        api_config["params"]["num"] = num
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")        
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data      
        # 处理返回数据
        try:
            result_msg = f"{server}-{data.get('date')}-星期{data.get('week')}\n"
            result_msg += f"大战：{data.get('war')}\n"
            result_msg += f"战场：{data.get('battle')}\n"
            result_msg += f"阵营：{data.get('orecar')}\n"
            result_msg += f"宗门：{data.get('school')}\n"
            result_msg += f"驰援：{data.get('rescue')}\n"
            result_msg += f"画像：{data.get('draw')}\n"
            result_msg += f"宠物福缘：\n{data.get('luck')}\n"
            result_msg += f"家园声望：\n{data.get('card')}\n"
            result_msg += f"武林通鉴：\n{data.get('team')}\n"
            return_data["data"] = result_msg
            return_data["code"] = 200       
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data


    async def shapan(self,server: str = "眉间雪"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_shapan"]
        #更新参数
        api_config["params"]["serverName"] = server
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")         
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data        
        # 处理返回数据
        try:
            return_data["data"] = data.get("picUrl")
            return_data["code"] = 200       
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data


    async def shaohua(self):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3_shaohua"]
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")         
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data        
        # 处理返回数据
        try:
            return_data["data"] = data.get("text")
            return_data["code"] = 200       
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data


    async def jigai(self):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3_jigai"]
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")         
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data 
        # 处理返回数据
        try:
            result_msg = f"剑网三最近技改\n"
            for i, item in enumerate(data[:2], 1):
                result_msg += f"{i}. {item.get('title', '无标题')}\n"
                result_msg += f"时间：{item.get('time', '未知时间')}\n"
                result_msg += f"链接：{item.get('url', '无链接')}\n\n"
            return_data["data"] = result_msg
            return_data["code"] = 200          
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "处理接口返回信息时出错"
        return return_data
    

    async def jinjia(self, server: str = "眉间雪"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_jinjia"]
        #更新参数
        api_config["params"]["serverName"] = server
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data 
        # 加载模板
        try:
            return_data["temp"] = load_template("jinjia.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data
        # 准备模板渲染数据
        try:
            return_data["data"] = {
                "items": data,
                "server": api_config["params"]["serverName"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            } 
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "系统错误：模板渲染数据准备失败"
            return return_data      
        return_data["code"] = 200       
        return return_data


    async def qiyu(self, adventureName: str = "阴阳两界", serverName: str = "眉间雪"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_qiyu"]
        #更新参数
        api_config["params"]["adventureName"] = adventureName
        api_config["params"]["serverName"] = serverName
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data
        # 格式化时间
        for item in data:
            if "time" in item:
                item["time"] = datetime.fromtimestamp(item["time"]/1000).strftime("%Y-%m-%d %H:%M:%S")
        # 加载模板
        try:
            return_data["temp"] = load_template("qiyuliebiao.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data
        # 准备模板渲染数据
        try:            
            return_data["data"] = {
                "items": data,
                "server": serverName,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ,"qiyuname": adventureName
            }
        except Exception as e:
            logger.error(f"处理数据时出错: {e}")
            return_data["msg"] = "系统错误：模板渲染数据准备失败"
            return return_data      
        return_data["code"] = 200       
        return return_data
    

    async def SearchData(self):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_SearchData"]
        # 获取数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "获取接口信息失败"
            return  return_data
        # 提取数据
        try:
            extracted_data = flatten_field(data, "dataModels")
        except FileNotFoundError as e:
            logger.error(f"提取数据失败: {e}")
            return_data["msg"] = "提取指定数据字段失败"
            return return_data 
        # 准备SQL和批量数据
        sql = """
        INSERT INTO searchdata 
        (typeName, name, showName, picUrl, searchId, searchDescType) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values_list = [
            (
                item['typeName'],
                item['name'],
                item['showName'],
                item['picUrl'],
                item['searchId'],
                item['searchDescType']
            )
            for item in extracted_data
        ]
        # 插入数据
        try:
            await self.__db.truncate_table("searchdata")
            await self.__db.executemany(sql, values_list)
        except FileNotFoundError as e:
            logger.error(f"数据插入失败: {e}")
            return_data["msg"] = "数据插入数据库失败"
            return return_data
        return_data["msg"] = f"成功批量插入 {len(extracted_data)} 条数据！"
        return_data["code"] = 200       
        return return_data
    

    async def wujia(self,Name: str = "秃盒"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3box_exterior"]
        #更新参数
        api_config["params"]["keyword"] = Name
        # 获取查找信息
        data = await self.__api.get(api_config["url"],api_config["params"],"data")
        if data["total"] == 0:
            try:
                sql = "SELECT showName, searchId FROM searchdata WHERE name = %s OR showName = %s"
                sqldata = await self.__db.fetch_one(sql, (Name,Name)) 
                searchId=sqldata["searchId"]
                showName=sqldata["showName"]
                return_data["data"]["searchId"]=searchId
                return_data["data"]["showName"]=showName
            except Exception as e:
                logger.error(f"获取外观信息错误: {e}")
                return_data["msg"] = "未找到该外观信息"
                return  return_data
        else:
            # 查询魔盒获取外观名称
            try:  
                showName=data["list"][0]["name"]
                return_data["data"]["showName"]=showName
            except Exception as e:
                logger.error(f"获取外观名称错误: {e}")
                return_data["msg"] = "未找到该外观信息"
                return  return_data
            # 查询爱剑三获取外观ID
            try:
                sql = "SELECT searchId FROM searchdata WHERE showName=%s"
                sqldata = await self.__db.fetch_one(sql, (return_data["data"]["showName"],))   
                searchId=sqldata["searchId"]
                return_data["data"]["searchId"]=searchId
            except Exception as e:
                logger.error(f"获取外观ID错误: {e}\n{return_data['data']['showName']}")
                return_data["msg"] = "未找到该外观信息"
                return  return_data

        #在配置文件中获取接口配置
        api_config = self.__api_config["aijx3_GoodsDetail"]
        #更新参数
        api_config["params"]["goodsName"] = showName
        # 获取数据外观详细数据
        data = await self.__api.post(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "获取外观详细数据失败"
            return  return_data
        # 提取外观详细数据
        try:
            imgs = data.get("imgs", [])
            return_data["data"]["goodsDesc"]=data.get("goodsDesc", "无描述")
            return_data["data"]["publishTime"]=data.get("publishTime", "无价格")
            return_data["data"]["priceNum"]=data.get("priceNum", 0)
            return_data["data"]["goodsId"]=data.get("goodsId", "无数据")
            return_data["data"]["imgs"]=imgs[0] if imgs else ""
            return_data["data"]["goodsAlias"]=data.get("goodsAlias", "无别名")
        except Exception as e:
            logger.error(f"提取外观详细数据失败: {e}")
            return_data["msg"] = "提取外观详细数据失败"
            return  return_data

        # 查询万宝楼数据（公示和在售）
        wbl_data = await self.__get_wbl_data(searchId)
        if not wbl_data:
            return_data["msg"] = "获取万宝楼数据失败"
            return  return_data
        if wbl_data:
            return_data["data"]["wblgs"]=wbl_data["wblgs"]
            return_data["data"]["wblzs"]=wbl_data["wblzs"]
            return_data["msg"] = "获取万宝楼数据完成"
        # 加载模板
        try:
            return_data["temp"] = load_template("wujia.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data
        return_data["code"] = 200   
        return return_data
    
    async def __get_wbl_data(self,search_id):
        """获取万宝楼数据（公示和在售）"""
        try:
            #在配置文件中获取接口配置
            api_config = self.__api_config["aijx3_wblwg"]
            #更新参数
            api_config["params"]["searchId"] = [search_id]
            # 获取公示数据 
            api_config["params"]["tradeStatus"] = "3"
            datawblgs = await self.__api.post(api_config["url"], api_config["params"], "data")
            # 获取在售数据
            api_config["params"]["tradeStatus"] = "5"
            datawblzs = await self.__api.post(api_config["url"], api_config["params"], "data")
            
            return {
                "wblgs": await self.__process_wbl_records(datawblgs.get("records", [])),
                "wblzs": await self.__process_wbl_records(datawblzs.get("records", []))
            }
        except Exception as e:
            logger.error(f"获取万宝楼数据出错: {e}")
            return None
    
    async def __process_wbl_records(self,records):
        """处理万宝楼记录数据"""
        processed = []
        for record in records:
            try:
                # 转换时间戳为可读格式
                timestamp = record.get("replyTime", 0)
                dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else datetime.now()
                
                processed.append({
                    "priceNum": record.get("priceNum", 0),
                    "belongQf2": record.get("belongQf2", "无数据"),
                    "replyTime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "discountRate": record.get("discountRate", 0.0),
                })
            except Exception as e:
                logger.error(f"处理万宝楼记录出错: {e}")
                continue
        
        return processed
    
    async def jiaoyihang(self,Name: str = "守缺式",server: str = "梦江南"):
        return_data = {
            "code": 0,
            "msg": "功能函数未执行",
            "data": {}
        }
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3box_item"]
        #更新参数
        api_config["params"]["keyword"] = Name
        # 获取多页查找信息
        data = await self.__api.all_pages("GET",api_config["url"],api_config["params"],"data","data")
        if not data:
            logger.error(f"获取多页数据失败")
            return_data["msg"] = "未找到该物品"
            return  return_data
        # 提取指定字段
        fields = ["IconID", "Name","id"]
        result = extract_fields(data, fields)
        if not data:
            logger.error(f"提取字段失败")
            return_data["msg"] = "未找到该物品"
            return  return_data
        # 提取id列表
        lists_id = extract_field(result, "id")
        strlists_id = ",".join(str(x) for x in lists_id)
        logger.info(f"{strlists_id}")
        #在配置文件中获取接口配置
        api_config = self.__api_config["jx3box_itemprice"]
        #更新参数
        api_config["params"]["itemIds"] = strlists_id
        api_config["params"]["server"] = server
        # 获取数据
        data = await self.__api.get(api_config["url"],api_config["params"],"data")
        if not data:
            return_data["msg"] = "未找到在售物品"
            return  return_data
        #提取需要的字段
        fieldsjyh = ["ItemId", "SampleSize", "LowestPrice", "AvgPrice", "Date"]
        resultjyh = [{f: v[f] for f in fieldsjyh} for v in data.values()]
        #合并表格数据
        # 先建立一个字典映射，加快查找
        map_result = {item["id"]: {"IconID": item["IconID"], "Name": item["Name"]} for item in result}
        # 遍历 resultjyh，合并字段
        for item in resultjyh:
            if item["ItemId"] in map_result:
                item.update(map_result[item["ItemId"]])
        #处理数据
        for item in resultjyh:
            item["LowestPrice"] = gold_to_string(item["LowestPrice"])
            item["AvgPrice"] = gold_to_string(item["AvgPrice"])
            item["IconID"] = f"https://icon.jx3box.com/icon/{item['IconID']}.png"
        # 准备模板渲染数据
        return_data["data"] = {
            "items": resultjyh,
            "server": server,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        } 
        # 加载模板
        try:
            return_data["temp"] = load_template("jiaoyihang.html")
        except FileNotFoundError as e:
            logger.error(f"加载模板失败: {e}")
            return_data["msg"] = "系统错误：模板文件不存在"
            return return_data 
        return_data["code"] = 200
        return return_data
