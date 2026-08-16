import os
import random
import time
import psycopg2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "post123"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

PRODUCTS = [
    ("Laptop", 55000.00),
    ("Wireless Mouse", 1200.00),
    ("Keyboard", 2500.00),
    ("Headphones", 3500.00),
    ("Monitor", 15000.00),
    ("Webcam", 4500.00),
    ("USB Cable", 500.00),
    ("Smartphone", 30000.00),
]

STATUSES = [
    "Pending",
    "Processing",
    "Shipped",
    "Completed",
]

INSERT_QUERY = """
    INSERT INTO orders
        (customer_id, product_name, quantity, price, order_status)
    VALUES (%s, %s, %s, %s, %s)
"""

def generate_order():
    customer_id = random.randint(101, 110)
    product_name, price = random.choice(PRODUCTS)
    quantity = random.randint(1, 5)
    order_status = random.choice(STATUSES)

    return (
        customer_id,
        product_name,
        quantity,
        price,
        order_status
    )

def insert_orders(cursor, orders):
    cursor.executemany(INSERT_QUERY, orders)

def main(rate=100):
    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        interval = 1.0 / rate
        total_orders = 0

        print(f"Order Generator Started - {rate} orders/second")
        print("Press Ctrl+C to stop.")

        while True:
            batch_start = time.time()

            orders = [generate_order() for _ in range(rate)]

            insert_orders(cursor, orders)
            connection.commit()

            total_orders += len(orders)

            print(f"Inserted {len(orders)} orders | Total: {total_orders}")

            elapsed = time.time() - batch_start

            if elapsed < 1:
                time.sleep(1 - elapsed)

    except KeyboardInterrupt:
        print("\nOrder Generator stopped.")
        print(f"Total orders generated: {total_orders}")

    except Exception as error:
        print("Error:", error)

        if connection:
            connection.rollback()

    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main(rate=100)