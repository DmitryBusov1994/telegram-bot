import asyncpg
from config import DATABASE_URL

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    # Таблица пользователей
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            free_attempts INTEGER DEFAULT 3,
            paid_attempts INTEGER DEFAULT 0,
            subscription_end TIMESTAMP
        )
    ''')
    # Таблица платежей
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            user_id BIGINT,
            amount INTEGER,
            status TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    ''')
    # Таблица истории поисков
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            query TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    ''')
    await conn.close()

async def get_user(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    await conn.close()
    return user

async def update_user(user_id: int, **kwargs):
    conn = await asyncpg.connect(DATABASE_URL)
    set_clause = ', '.join([f"{key} = ${i+1}" for i, key in enumerate(kwargs)])
    values = list(kwargs.values()) + [user_id]
    await conn.execute(f'UPDATE users SET {set_clause} WHERE user_id = ${len(kwargs)+1}', *values)
    await conn.close()

async def create_payment(payment_id: str, user_id: int, amount: int):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO payments (payment_id, user_id, amount, status)
        VALUES ($1, $2, $3, 'pending')
    ''', payment_id, user_id, amount)
    await conn.close()