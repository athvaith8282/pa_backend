import aiosqlite
from config import SQLITE_FILEPATH

async def get_sqlite_conn():
    conn = await aiosqlite.connect(SQLITE_FILEPATH)
    return conn

async def get_distinct_thread_ids(db_path: str = SQLITE_FILEPATH)->list[str]:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT DISTINCT thread_id FROM checkpoints") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]