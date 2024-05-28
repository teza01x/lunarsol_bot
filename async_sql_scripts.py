import aiosqlite
import asyncio
from config import *


async def check_user_exists(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE user_id = ?", (user_id,))
            user = await result.fetchall()
        return bool(len(user))


async def add_user_to_db(user_id, username):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO user (user_id, username, menu_status, verified_status) VALUES(?, ?, ?, ?)",
                (user_id, username, 0, 0))
            await conn.commit()


async def update_username(user_id, username):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET username = ? WHERE user_id = ?", (username, user_id,))
            await conn.commit()


async def change_menu_status(user_id, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET menu_status = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def get_user_menu_status(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT menu_status FROM user WHERE user_id = ?", (user_id,))
            user_status = await result.fetchone()
            return user_status[0]


async def get_verified_status(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT verified_status FROM user WHERE user_id = ?", (user_id,))
            verified_status = await result.fetchone()
            return verified_status[0]


async def change_verified_status(user_id, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET verified_status = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def get_all_verified_users():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT username FROM user WHERE verified_status = ?", (2,))
            all_users = await result.fetchall()
            return [users[0] for users in all_users]


async def change_verified_username_status(username, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET verified_status = ? WHERE username = ?", (status, username,))
            await conn.commit()


async def get_all_users():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user")
            all_users = await result.fetchall()
            return [users[0] for users in all_users]
