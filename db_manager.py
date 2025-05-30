import sqlite3
import os

DATABASE_NAME = "kasir.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE_NAME):
        print(f"[INFO]: Database '{DATABASE_NAME}' sudah ada.")
    else:
        print(f"[INFO]: Membuat database '{DATABASE_NAME}'...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    if not os.path.exists(DATABASE_NAME):
        print(f"[SUCCESS]: Database '{DATABASE_NAME}' berhasil dibuat.")
        
def add_menu_item(name, image_path, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO menu_items (name, image, price)
            VALUES (?, ?, ?)
        ''', (name, image_path, price))
        conn.commit()
        print(f"[INFO]: Item Menu ditambahkan: {name}, Gambar: {image_path}, Harga: {price}")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"[ERROR]: Gagal menambahkan item menu: {e}")
        return None
    finally:
        conn.close()
        
def get_all_menu_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, image, price FROM menu_items ORDER BY name")
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

if __name__ == "__main__":
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        print(f"[SUCCESS]: Database '{DATABASE_NAME}' berhasil dihapus untuk pengujian.")
    init_db()