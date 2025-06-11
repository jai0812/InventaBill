import sqlite3
import os

# Set up database path (relative to project root)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'inventabill.db')

def get_connection():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def initialize_db():
    """Create the products table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def initialize_sales_table():
    """Create the sales table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            items TEXT,
            subtotal REAL,
            cgst REAL,
            sgst REAL,
            total REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, category, price, quantity):
    """Insert a new product into the products table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, category, price, quantity)
        VALUES (?, ?, ?, ?)
    ''', (name, category, price, quantity))
    conn.commit()
    conn.close()

# Optional: fetch all products (can be used for testing)
def fetch_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

if __name__ == "__main__":
    initialize_db()
    initialize_sales_table()
    print("Database initialized and sales table created!")

    # # Optional: Add test products for quick setup (uncomment to use)
    # add_product("Milk", "Grocery", 40.0, 100)
    # add_product("Pen", "Stationery", 10.0, 200)
    # print("Sample products added!")
