from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "enterprise_ops.db"
DB.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB) as conn:
    conn.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS inventory;
    DROP TABLE IF EXISTS customers;
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT NOT NULL
    );
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY,
        sku TEXT NOT NULL,
        city TEXT NOT NULL,
        stock_quantity INTEGER NOT NULL,
        UNIQUE(sku, city)
    );
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        sku TEXT NOT NULL,
        city TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        order_value REAL NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );
    """)
    customers = [(i, f"Customer {i}", "Seattle" if i % 2 else "Portland") for i in range(1, 11)]
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers)
    inventory = [
        (1, "SKU-90210", "Seattle", 80),
        (2, "SKU-10001", "Seattle", 25),
        (3, "SKU-10002", "Seattle", 120),
        (4, "SKU-90210", "Portland", 40),
        (5, "SKU-10001", "Portland", 60),
        (6, "SKU-10002", "Portland", 15),
        (7, "SKU-77777", "Seattle", 9),
        (8, "SKU-77777", "Portland", 31),
        (9, "SKU-55555", "Seattle", 200),
        (10, "SKU-55555", "Portland", 175),
    ]
    conn.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?)", inventory)
    orders = [
        (4492, 1, "SKU-90210", "Seattle", 50, 1250.00),
        (4493, 2, "SKU-10001", "Portland", 10, 420.00),
        (4494, 3, "SKU-10002", "Seattle", 20, 880.00),
        (4495, 4, "SKU-77777", "Portland", 8, 310.00),
        (4496, 5, "SKU-55555", "Seattle", 60, 2400.00),
        (4497, 6, "SKU-90210", "Portland", 15, 375.00),
        (4498, 7, "SKU-10001", "Seattle", 4, 168.00),
        (4499, 8, "SKU-10002", "Portland", 12, 528.00),
        (4500, 9, "SKU-77777", "Seattle", 3, 116.25),
        (4501, 10, "SKU-55555", "Portland", 30, 1200.00),
    ]
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders)
    conn.commit()
print(f"Seeded {DB}")
