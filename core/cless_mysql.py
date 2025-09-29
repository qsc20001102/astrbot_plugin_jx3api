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
        """执行单条 SQL（insert/update/delete）"""
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
        """清空指定表的内容"""
        await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = f"TRUNCATE TABLE `{table_name}`"
                await cursor.execute(sql)
                await conn.commit()
                return True
