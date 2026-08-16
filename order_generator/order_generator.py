import os
import random
import psycopg2

# PostgreSQL connection (reads from environment variables, falls back to defaults)
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
    RETURNING order_id, order_timestamp;
"""


def generate_order():
    """Generate one random order as a tuple."""
    customer_id = random.randint(101, 110)
    product_name, price = random.choice(PRODUCTS)
    quantity = random.randint(1, 5)
    order_status = random.choice(STATUSES)
    return (customer_id, product_name, quantity, price, order_status)


def insert_orders(orders):
    """Insert one or more orders using a single reused connection.

    Returns a list of (order_id, order_timestamp) for each inserted order.
    """
    results = []
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        with connection:
            with connection.cursor() as cursor:
                for order in orders:
                    cursor.execute(INSERT_QUERY, order)
                    results.append(cursor.fetchone())
        print(f"Inserted {len(results)} order(s) successfully!")
    except Exception as error:
        print("Error:", error)
        # `with connection` already rolls back on exception,
        # but we guard here in case the error happened before that context.
        if connection and not connection.closed:
            connection.rollback()
    finally:
        if connection:
            connection.close()
    return results


def print_order(order, order_id=None, timestamp=None):
    customer_id, product_name, quantity, price, order_status = order
    print("\nOrder:")
    print("  Customer ID:", customer_id)
    print("  Product:", product_name)
    print("  Quantity:", quantity)
    print("  Price:", price)
    print("  Status:", order_status)
    if order_id is not None:
        print("  Order ID:", order_id)
    if timestamp is not None:
        print("  Timestamp:", timestamp)


def main(num_orders=1):
    print(f"Order Generator Started — generating {num_orders} order(s)")

    orders = [generate_order() for _ in range(num_orders)]
    for order in orders:
        print_order(order)

    results = insert_orders(orders)

    for order, result in zip(orders, results):
        order_id, timestamp = result
        print_order(order, order_id, timestamp)


if __name__ == "__main__":
    # Change num_orders to generate/insert multiple orders in one run
    main(num_orders=1)