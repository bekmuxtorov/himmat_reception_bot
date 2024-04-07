from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE 
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_groups(self):
        sql = """
        CREATE TABLE IF NOT EXISTS groups(
            id SERIAL PRIMARY KEY,
            by_user_id BIGINT NOT NULL,
            by_user_name VARCHAR(255) NOT NULL,
            group_id BIGINT NOT NULL,
            group_name VARCHAR(255) NULL,
            created_at DATETIME NOT NULL DEFAULT NOW(), 
           )
        """

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_group(self, by_user_id, by_user_name, group_id, created_at):
        sql = """
            INSERT INTO groups (by_user_id, by_user_name, group_id, created_at) 
            VALUES ($1, $2, $3, $4) returning *;
        """
        return await self.execute(self, by_user_id, by_user_name, group_id, created_at, fetchrow=True)

    async def select_all_groups(self):
        sql = "SELECT * FROM groups"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "by_user_name": item[2],
                "group_id": item[3],
                "group_name": item[4],
                "created_at": item[5]
            } for item in data
        ] if data else None

    async def select_group(self, **kwargs):
        sql = """
            SELECT * FROM groups WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "by_user_id": data[1],
            "by_user_name": data[2],
            "group_id": data[3],
            "group_name": data[4],
            "created_at": data[5],
        } if data else None

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
