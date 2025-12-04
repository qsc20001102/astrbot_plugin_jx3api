import aiosqlite

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

    async def fetch_one(self, sql: str, params=None):
        await self.init()
        async with self.conn.execute(sql, params or ()) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetch_all(self, sql: str, params=None):
        await self.init()
        async with self.conn.execute(sql, params or ()) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def execute(self, sql: str, params=None):
        await self.init()
        async with self.conn.execute(sql, params or ()):
            await self.conn.commit()
        return True

    async def executemany(self, sql: str, params_list):
        await self.init()
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
