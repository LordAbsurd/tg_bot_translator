import mysql.connector
from mysql.connector import Error
from datetime import datetime
import dotenv
import os

dotenv.load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DB = os.getenv('MYSQL_DB', 'test')
MYSQL_USER = os.getenv('MYSQL_USER', 'bot')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '12345678')
MYSQL_AUTH_PLUGIN = os.getenv('MYSQL_AUTH_PLUGIN', 'mysql_native_password')

MYSQL_CONFIG = {'host': MYSQL_HOST, 'port': MYSQL_PORT, 'database': MYSQL_DB, 'user': MYSQL_USER, 'password': MYSQL_PASSWORD, 'auth_plugin': MYSQL_AUTH_PLUGIN}

class User:
    def __init__(self, id, user_lang, translate_lang):
        self.id = id
        self.user_lang = user_lang
        self.translate_lang = translate_lang

def create_tables():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                user_lang VARCHAR(10),
                translate_lang VARCHAR(10)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error creating tables: {e}")

def check_user_exists(user_id) -> bool:
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        print(f"Error checking user existence: {e}")
        return False

def create_user(user_id, user_lang=None, translate_lang=None):
    try:
        now = datetime.now()
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, user_lang, translate_lang)
            VALUES (%s, %s, %s)
        ''', (user_id, user_lang, translate_lang))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error creating user: {e}")

def get_user(user_id):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return User(*result)
        return None
    except Error as e:
        print(f"Error getting user: {e}")
        return None

def update_user_data(user_id, **kwargs):
    if not kwargs:
        return
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        set_clause = ', '.join(f"{k} = %s" for k in kwargs.keys())
        values = list(kwargs.values())
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = %s", values)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error updating user data: {e}")

#db telegram update id 
def edit_update(update_id):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE updates SET id = %s", (update_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error editing update: {e}")

def get_update():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM updates")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result else None
    except Error as e:
        print(f"Error getting update: {e}")
        return None

def check_update():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS updates (id INT PRIMARY KEY)")
        cursor.execute("SELECT id FROM updates")
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO updates (id) VALUES (%s)", (0,))
            conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error checking update: {e}")

#reload users table run mysql_db_functions.py as main
def reload_users_table():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        cursor.close()
        conn.close()
        create_tables()
    except Error as e:
        print(f"Error reloading users table: {e}")


if __name__ == '__main__':
    reload_users_table()