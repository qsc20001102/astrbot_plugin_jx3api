import aiomysql


class AsyncMySQL:
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.pool = None

    async def init_pool(self):
        """初始化连接池"""
        if self.pool is None:
            self.pool = await aiomysql.create_pool(**self.db_config)

    async def close_pool(self):
        """关闭连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    async def fetch_one(self, sql: str, params=None):
        """查询单条数据"""
        await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params or ())
                return await cursor.fetchone()

    async def fetch_all(self, sql: str, params=None):
        """查询多条数据"""
        await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params or ())
                return await cursor.fetchall()

    async def execute(self, sql: str, params=None):
        """执行 SQL（insert/update/delete）"""
        await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, params or ())
                await conn.commit()
                return cursor.rowcount

    async def executemany(self, sql: str, params_list):
        """批量执行 SQL"""
        await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.executemany(sql, params_list)
                await conn.commit()
                return cursor.rowcount

    async def truncate_table(self, table_name: str):
        """清空指定表"""
        await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = f"TRUNCATE TABLE `{table_name}`"
                await cursor.execute(sql)
                await conn.commit()
                return True

    # ----------------------------------------------------------------------
    # 新增：自动生成 SQL 的增删改功能
    # ----------------------------------------------------------------------

    async def insert_record(self, table: str, data: dict):
        """插入记录：data 是 dict"""
        keys = ", ".join(f"`{k}`" for k in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO `{table}` ({keys}) VALUES ({placeholders})"
        return await self.execute(sql, tuple(data.values()))

    async def update_record(self, table: str, data: dict, where: dict):
        """更新记录：data、where 都是 dict"""
        set_clause = ", ".join(f"`{k}`=%s" for k in data.keys())
        where_clause = " AND ".join(f"`{k}`=%s" for k in where.keys())

        sql = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"

        params = tuple(data.values()) + tuple(where.values())
        return await self.execute(sql, params)

    async def delete_record(self, table: str, where: dict):
        """删除记录：where 是 dict"""
        where_clause = " AND ".join(f"`{k}`=%s" for k in where.keys())
        sql = f"DELETE FROM `{table}` WHERE {where_clause}"
        return await self.execute(sql, tuple(where.values()))
