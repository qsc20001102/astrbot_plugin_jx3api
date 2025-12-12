import aiosqlite
import logging
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("AsyncSQLite")


class AsyncSQLite:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    async def init(self):
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    def _format_sql(self, sql: str, params):
        """生成完整 SQL（安全打印）"""

        if not params:
            return sql

        def escape(value):
            if value is None:
                return "NULL"
            if isinstance(value, (int, float)):
                return str(value)
            # 转义单引号
            value = str(value).replace("'", "''")
            return f"'{value}'"

        final_sql = sql
        for v in params:
            final_sql = final_sql.replace("?", escape(v), 1)

        return final_sql

    async def _log_and_execute(self, sql: str, params=None, fetch: str = None):
        await self.init()

        # 打印原始 SQL 和参数
        logger.debug(f"[SQLite] SQL Raw: {sql}")
        logger.debug(f"[SQLite] Params: {params}")

        # 打印最终执行 SQL
        final_sql = self._format_sql(sql, params or ())
        logger.debug(f"[SQLite] SQL Final: {final_sql}")

        async with self.conn.execute(sql, params or ()) as cursor:
            if fetch == "one":
                row = await cursor.fetchone()
                return dict(row) if row else None

            if fetch == "all":
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

            await self.conn.commit()
            return True

    async def fetch_one(self, sql: str, params=None):
        return await self._log_and_execute(sql, params, fetch="one")

    async def fetch_all(self, sql: str, params=None):
        return await self._log_and_execute(sql, params, fetch="all")

    async def execute(self, sql: str, params=None):
        return await self._log_and_execute(sql, params)

    async def executemany(self, sql: str, params_list):
        await self.init()
        logger.debug(f"[SQLite] SQL (executemany): {sql}")
        logger.debug(f"[SQLite] Params List: {params_list}")
        await self.conn.executemany(sql, params_list)
        await self.conn.commit()
        return True

    async def insert_record(self, table: str, data: dict):
        keys = ", ".join(f"`{k}`" for k in data.keys())
        placeholders = ", ".join(['?'] * len(data))
        sql = f"INSERT INTO `{table}` ({keys}) VALUES ({placeholders})"
        return await self.execute(sql, tuple(data.values()))

    async def update_record(self, table: str, data: dict, where: dict):
        set_clause = ", ".join(f"`{k}`=?" for k in data.keys())
        where_clause = " AND ".join(f"`{k}`=?" for k in where.keys())
        sql = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(where.values())
        return await self.execute(sql, params)

    async def delete_record(self, table: str, where: dict):
        where_clause = " AND ".join(f"`{k}`=?" for k in where.keys())
        sql = f"DELETE FROM `{table}` WHERE {where_clause}"
        return await self.execute(sql, tuple(where.values()))

    async def clear_table(self, table: str):
        sql = f"DELETE FROM `{table}`"
        return await self.execute(sql)
