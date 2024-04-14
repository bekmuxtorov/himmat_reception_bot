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
        CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        gender VARCHAR(128) NULL,
        created_at timestamp with time zone NOT NULL DEFAULT NOW()
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
        created_at timestamp with time zone NOT NULL DEFAULT NOW(),
        for_whom VARCHAR(255) NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_questions(self):
        sql = """
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                sender_id BIGINT NOT NULL,
                sender_full_name VARCHAR(255) NOT NULL,
                question VARCHAR(255) NOT NULL,
                answer VARCHAR(255) NULL,
                respondent_id BIGINT NULL,
                respondent_full_name VARCHAR(255) NULL,
                created_at timestamp with time zone NOT NULL DEFAULT NOW()
            );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_group(self, by_user_id, by_user_name, group_id, group_name, created_at, for_whom):
        sql = """
            INSERT INTO groups (by_user_id, by_user_name, group_id, group_name, created_at, for_whom) 
            VALUES ($1, $2, $3, $4, $5, $6) returning *;
        """
        return await self.execute(sql, by_user_id, by_user_name, group_id, group_name, created_at, for_whom, fetchrow=True)

    async def select_all_groups(self):
        sql = "SELECT * FROM groups WHERE for_whom in ('man_users', 'woman_users');"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "by_user_name": item[2],
                "group_id": item[3],
                "group_name": item[4],
                "created_at": item[5],
            } for item in data
        ] if data else None

    async def select_group(self, **kwargs):
        sql = """
            SELECT * FROM groups  WHERE 
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
            "for_whom": data[6]
        } if data else None

    async def select_group_by_for_whom(self, for_whom):
        sql = """
            select * from groups where for_whom=$1 order by created_at desc limit 1 
        """
        data = await self.execute(sql, for_whom, fetchrow=True)
        return {
            "id": data[0],
            "by_user_id": data[1],
            "by_user_name": data[2],
            "group_id": data[3],
            "group_name": data[4],
            "created_at": data[5],
            "for_whom": data[6]
        } if data else None

    async def delete_group(self, **kwargs):
        sql = "DELETE FROM groups WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        await self.execute(sql, *parameters, execute=True)

    async def add_question(self, sender_id, sender_full_name, question, created_at):
        sql = """
            INSERT INTO questions (sender_id, sender_full_name, question, created_at)
            VALUES ($1, $2, $3, $4) returning *;
        """
        return await self.execute(sql, sender_id, sender_full_name, question, created_at, fetchrow=True)

    async def update_question(self, id, answer, respondent_id, respondent_full_name):
        sql = "UPDATE question SET answer=$2, respondent_id=$3, respondent_full_name=$4, WHERE telegram_id=$1"
        return await self.execute(sql, id, answer, respondent_id, respondent_full_name, execute=True)

    async def select_question(self, **kwargs):
        sql = """
            SELECT * FROM questions WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "sender_id": data[1],
            "sender_full_name": data[2],
            "question": data[3],
            "answer": data[4],
            "respondent_id": data[5],
            "respondent_full_name": data[6],
            "created_at": data[7]
        } if data else None

    async def add_user(self, full_name, username, telegram_id, created_at):
        sql = "INSERT INTO users (full_name, username, telegram_id, created_at) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, username, telegram_id, created_at, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "full_name": data[1],
            "username": data[2],
            "telegram_id": data[3],
            "gender": data[4],
            "created_at": data[5]
        } if data else None

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def update_user_gender(self, gender, telegram_id):
        sql = "UPDATE users SET gender=$1 WHERE telegram_id=$2"
        return await self.execute(sql, gender, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
