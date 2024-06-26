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
                user_id INT REFERENCES users(telegram_id),
                sender_full_name VARCHAR(255) NOT NULL,
                question VARCHAR(255) NOT NULL,
                answer VARCHAR(255) NULL,
                respondent_full_name VARCHAR(255) NULL,
                response_date timestamp with time zone null,
                created_at timestamp with time zone NOT NULL DEFAULT NOW()
            );
        """
        await self.execute(sql, execute=True)

    async def create_table_applications(self):
        sql = """
        CREATE TABLE IF NOT EXISTS applications(
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) NULL,
            course_id INT REFERENCES courses(id) NULL,
            is_accepted BOOL NULL,
            is_enter_group BOOL NULL,
            applied_date timestamp with time zone NULL,
            created_at timestamp with time zone NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_courses(self):
        sql = """
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            description VARCHAR(255),
            for_man_group_id varchar(255),
            for_man_group_name varchar(255) NULL,
            for_woman_group_id varchar(255),
            for_woman_group_name varchar(255) NULL, 
            created_at timestamp with time zone NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_enrollments(self):
        sql = """
            CREATE TABLE IF NOT EXISTS enrollments(
                id SERIAL PRIMARY KEY,
                user_id INT FOREIGN KEY REFERENCES users(telegram_id),
                course_id INT FOREIGN KEY REFERENCES courses(id),  
                created_at timestamp with time zone NOT NULL DEFAULT NOW()
            )
        """
        await self.execute(sql, execute=True)

    async def create_table_topics(self):
        sql = """
        CREATE TABLE IF NOT EXISTS topics(
        id SERIAL PRIMARY KEY,
        topic_id BIGINT NOT NULL,
        topic_name VARCHAR(255) NULL,
        topic_created_group_id BIGINT NOT NULL,
        created_at timestamp with time zone NOT NULL DEFAULT NOW(),
        for_purpose VARCHAR(255) NULL
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

    # For groups
    async def add_group(self, by_user_id, by_user_name, group_id, group_name, created_at, for_whom):
        sql = """
            INSERT INTO groups (by_user_id, by_user_name, group_id, group_name, created_at, for_whom) 
            VALUES ($1, $2, $3, $4, $5, $6) returning *;
        """
        return await self.execute(sql, by_user_id, by_user_name, group_id, group_name, created_at, for_whom, fetchrow=True)

    async def select_all_groups(self):
        sql = "SELECT * FROM groups WHERE for_whom in ('man_users', 'woman_users', 'mixed_users');"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "id": item[0],
                "by_user_name": item[2],
                "group_id": item[3],
                "group_name": item[4],
                "created_at": item[5],
                "for_whom": item[6],

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

    # For applications
    async def add_application(self, user_id, course_id, created_at):
        sql = """
            INSERT INTO applications (user_id, course_id, created_at)
            VALUES ($1, $2, $3) returning *;
        """
        return await self.execute(sql, user_id, course_id, created_at, fetchrow=True)

    async def update_application_field(self, application_id, field_name, value):
        sql = f"UPDATE applications SET {field_name}=$3 WHERE id=$1"
        return await self.execute(sql, application_id, field_name, value, execute=True)

    async def select_application(self, **kwargs):
        sql = """
            SELECT * FROM applications WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "user_id": data[1],
            "course_id": data[2],
            "is_accepted": data[3],
            "is_enter_group": data[4],
            "applied_date": data[5],
            "created_at": data[6]
        } if data else None

    # For courses
    async def add_course(self, name, description, for_man_group_id, for_man_group_name, for_woman_group_id, for_woman_group_name, created_at):
        sql = """
        INSERT INTO courses (name, description, for_man_group_id, for_man_group_name, for_woman_group_id, for_woman_group_name, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7) returning *;
        """
        return await self.execute(sql, name, description, for_man_group_id, for_man_group_name, for_woman_group_id, for_woman_group_name, created_at, fetchrow=True)

    async def select_all_courses(self):
        sql = """
            SELECT * FROM courses order by created_at desc;
        """
        data = await self.execute(sql, fetch=True)
        return [
            {
                "id": item[0],
                "name": item[1],
                "description": item[2],
                "for_man_group_id": item[3],
                "for_woman_group_id": item[4],
                "created_at": item[5],
            } for item in data
        ] if data else None

    async def select_course(self, **kwargs):
        sql = """
            SELECT * FROM courses WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "name": data[1],
            "description": data[2],
            "for_man_group_id": data[3],
            "for_woman_group_id": data[4],
            "created_at": data[5],
        } if data else None

    # For enrollments
    async def add_enrollment(self, user_id, course_id, created_at):
        sql = """
        INSERT INTO enrollments (user_id, course_id, created_at)
        VALUES ($1, $2, $3) returning *;
        """
        return await self.execute(sql, user_id, course_id, created_at, fetchrow=True)

    async def select_all_enrollments(self):
        sql = """
            SELECT * FROM enrollments order by created_at desc;
        """
        data = await self.execute(sql, fetch=True)
        return [
            {
                "id": item[0],
                "user_id": item[1],
                "course_id": item[2],
                "created_at": item[3],
            } for item in data
        ] if data else None

    # For questions
    async def add_question(self, sender_id, sender_full_name, question, created_at):
        sql = """
            INSERT INTO questions (sender_id, sender_full_name, question, created_at)
            VALUES ($1, $2, $3, $4) returning *;
        """
        data = await self.execute(sql, sender_id, sender_full_name, question, created_at, fetchrow=True)
        return data[0]

    async def update_question(self, id, answer, respondent_id, respondent_full_name):
        sql = "UPDATE questions SET answer=$2, respondent_id=$3, respondent_full_name=$4 WHERE id=$1"
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

    # For users
    async def add_user(self, full_name, username, telegram_id, created_at):
        sql = "INSERT INTO users (full_name, username, telegram_id, created_at) VALUES($1, $2, $3, $4) returning *"
        data = await self.execute(sql, full_name, username, telegram_id, created_at, fetchrow=True)
        return {
            "id": data[0],
        }

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

    async def update_user(self, field, new_value, telegram_id):
        sql = f"UPDATE users SET {field}=$1 WHERE telegram_id=$2"
        return await self.execute(sql, new_value, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)

    # for topics
    async def add_topic(self, topic_id, topic_name, topic_created_group_id, created_at, for_purpose):
        sql = """
            INSERT INTO topics (topic_id, topic_name, topic_created_group_id, created_at, for_purpose) 
            VALUES ($1, $2, $3, $4, $5) returning *;
        """
        return await self.execute(sql, topic_id, topic_name, topic_created_group_id, created_at, for_purpose, fetchrow=True)

    async def select_topic(self, **kwargs):
        sql = """
            SELECT * FROM topics  WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "topic_id": data[1],
            "topic_name": data[2],
            "topic_created_group_id": data[3],
            "created_at": data[4],
            "for_purpose": data[5]
        } if data else None

    async def get_topic_id(self, group_id, for_purpose):
        sql = """
            SELECT topic_id FROM topics WHERE topic_created_group_id=$1 and for_purpose=$2 LIMIT 1;
        """
        return await self.execute(sql, group_id, for_purpose, fetchval=True)
