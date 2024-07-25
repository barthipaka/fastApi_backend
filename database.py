import aiomysql
from fastapi import  Depends

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "db": "covalenseglobal",
    "autocommit": True,
}

# Create a database connection pool
async def get_database_pool():
    pool = await aiomysql.create_pool(**DATABASE_CONFIG)
    return pool

# Dependency to inject database connection pool
async def get_database_connection(pool = Depends(get_database_pool)):
    async with pool.acquire() as connection:
        async with connection.cursor(aiomysql.DictCursor) as cursor:
            yield cursor
