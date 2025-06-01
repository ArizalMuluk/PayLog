import os
import sqlite3
from datetime import datetime
import json

from kivy.utils import platform
if platform == "android":
    from android.storage import app_storage_path #type: ignore
    DATABASE_NAME = os.path.join(app_storage_path(), "kasir.db")
else:
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL 
        )
    ''')

    # Tambah tabel sales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            outlet_name TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL
        )
    ''')

    # Tambah tabel outlite
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outlite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
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

def add_table(name: str, status: str):
    """Menambahkan meja baru ke database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tables (name, status)
            VALUES (?, ?)
        ''', (name, status))
        conn.commit()
        print(f"[INFO]: Meja ditambahkan: {name}, Status: {status}")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"[ERROR]: Gagal menambahkan meja '{name}'. Nama meja mungkin sudah ada.")
        return None
    except sqlite3.Error as e:
        print(f"[ERROR]: Gagal menambahkan meja '{name}': {e}")
        return None
    finally:
        conn.close()

def get_all_tables():
    """Mengambil semua data meja dari database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status FROM tables ORDER BY name")
    tables = cursor.fetchall()
    conn.close()
    return [dict(table) for table in tables]

def update_table_status(name: str, new_status: str):
    """Memperbarui status meja berdasarkan namanya."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE tables
            SET status = ?
            WHERE name = ?
        ''', (new_status, name))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"[WARNING]: Tidak ada meja dengan nama '{name}' untuk diperbarui statusnya.")
            return False
        print(f"[INFO]: Status meja '{name}' diperbarui menjadi '{new_status}'")
        return True
    except sqlite3.Error as e:
        print(f"[ERROR]: Gagal memperbarui status meja '{name}': {e}")
        return False
    finally:
        conn.close()

def delete_table(name: str):
    """Menghapus meja berdasarkan namanya."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            DELETE FROM tables
            WHERE name = ?
        ''', (name,))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"[WARNING]: Tidak ada meja dengan nama '{name}' untuk dihapus.")
            return False
        print(f"[INFO]: Meja '{name}' berhasil dihapus.")
        return True
    except sqlite3.Error as e:
        print(f"[ERROR]: Gagal menghapus meja '{name}': {e}")
        return False
    finally:
        conn.close()

def save_sale(outlet_name, items, total):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sales (date, outlet_name, items, total)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            outlet_name,
            json.dumps(items),
            total
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"[ERROR]: Gagal menyimpan transaksi: {e}")
        return None
    finally:
        conn.close()

def get_all_sales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sales ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    sales = []
    for row in rows:
        item = dict(row)
        item['items'] = json.loads(item['items'])
        sales.append(item)
    return sales

def save_outlite(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO outlite (name, created_at)
            VALUES (?, ?)
        ''', (name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"[ERROR]: Gagal menyimpan outlet: {e}")
        return None
    finally:
        conn.close()

def get_last_outlite():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM outlite ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

if __name__ == "__main__":
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        print(f"[SUCCESS]: Database '{DATABASE_NAME}' berhasil dihapus untuk pengujian.")
    init_db()