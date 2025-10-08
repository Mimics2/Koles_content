import sqlite3

DATABASE_NAME = "bot_database.db"

def init_db():
    """Инициализирует базу данных и создает таблицу users."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            subscription_type TEXT,
            subscription_end_date TEXT,
            channels_attached INTEGER,
            posts_per_day INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    """Добавляет нового пользователя в базу данных."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Пользователь с ID {user_id} уже существует.")
    finally:
        conn.close()

def get_user(user_id):
    """Получает информацию о пользователе из базы данных."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

