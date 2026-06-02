import sqlite3
import pandas as pd
from pathlib import Path


DB_PATH = Path("data/insightguard.db")


def create_connection():
    """
    Creates a connection to the SQLite database.
    SQLite is a lightweight database stored as a local file.
    """

    connection = sqlite3.connect(DB_PATH)
    return connection


def create_sample_database():
    """
    Creates sample business tables and inserts sales data.

    Tables:
    1. customers
    2. products
    3. orders
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS products")

    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT,
            region TEXT,
            industry TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            unit_price REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            order_date TEXT,
            quantity INTEGER,
            revenue REAL,
            discount REAL,
            returned INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    """)

    customers = [
        (1, "Acme Corp", "North", "Retail"),
        (2, "Bright Health", "East", "Healthcare"),
        (3, "NovaTech", "West", "Technology"),
        (4, "GreenMart", "South", "Retail"),
        (5, "FinEdge", "North", "Finance"),
        (6, "UrbanStyle", "East", "E-commerce"),
        (7, "MediCore", "West", "Healthcare"),
        (8, "CloudNine", "South", "Technology")
    ]

    products = [
        (1, "Analytics Pro", "Software", 1200.00),
        (2, "DataSync Tool", "Software", 850.00),
        (3, "Support Plan", "Service", 300.00),
        (4, "Cloud Storage", "Cloud", 500.00),
        (5, "AI Insights Pack", "AI", 1500.00)
    ]

    orders = [
        (1, 1, 1, "2024-01-12", 2, 2400, 0.05, 0),
        (2, 2, 5, "2024-01-20", 1, 1500, 0.00, 0),
        (3, 3, 2, "2024-02-10", 4, 3400, 0.10, 0),
        (4, 4, 3, "2024-02-18", 3, 900, 0.00, 1),
        (5, 5, 4, "2024-03-05", 5, 2500, 0.05, 0),
        (6, 6, 1, "2024-03-21", 1, 1200, 0.00, 0),
        (7, 7, 5, "2024-04-09", 2, 3000, 0.15, 0),
        (8, 8, 2, "2024-04-15", 3, 2550, 0.05, 0),
        (9, 1, 4, "2024-05-01", 2, 1000, 0.00, 1),
        (10, 2, 3, "2024-05-19", 6, 1800, 0.10, 0),
        (11, 3, 5, "2024-06-08", 1, 1500, 0.00, 0),
        (12, 4, 1, "2024-06-25", 2, 2400, 0.05, 0),
        (13, 5, 2, "2024-07-11", 4, 3400, 0.10, 0),
        (14, 6, 4, "2024-07-30", 2, 1000, 0.00, 0),
        (15, 7, 3, "2024-08-14", 5, 1500, 0.05, 1),
        (16, 8, 5, "2024-08-22", 3, 4500, 0.10, 0),
        (17, 1, 2, "2024-09-03", 2, 1700, 0.00, 0),
        (18, 2, 1, "2024-09-18", 1, 1200, 0.00, 0),
        (19, 3, 4, "2024-10-06", 6, 3000, 0.15, 0),
        (20, 4, 5, "2024-10-27", 2, 3000, 0.05, 0),
        (21, 5, 3, "2024-11-09", 4, 1200, 0.00, 0),
        (22, 6, 2, "2024-11-20", 5, 4250, 0.10, 0),
        (23, 7, 1, "2024-12-02", 3, 3600, 0.05, 0),
        (24, 8, 4, "2024-12-17", 4, 2000, 0.00, 1)
    ]

    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)", orders)

    connection.commit()
    connection.close()


def execute_sql_query(query: str) -> pd.DataFrame:
    """
    Executes a SQL query and returns results as a Pandas DataFrame.
    """

    connection = create_connection()

    try:
        dataframe = pd.read_sql_query(query, connection)
    finally:
        connection.close()

    return dataframe


def get_database_schema() -> str:
    """
    Returns a simple schema description.
    This helps explain what tables and columns are available.
    """

    schema = """
    Tables:

    customers:
    - customer_id
    - customer_name
    - region
    - industry

    products:
    - product_id
    - product_name
    - category
    - unit_price

    orders:
    - order_id
    - customer_id
    - product_id
    - order_date
    - quantity
    - revenue
    - discount
    - returned
    """

    return schema