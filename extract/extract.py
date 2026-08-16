import os
import psycopg2


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "post123"),
    "port": int(os.getenv("DB_PORT", 5432)),
}


def extract_new_orders(last_order_id=0, batch_size=500):
    """
    Extract newly inserted orders from the orders table.

    Parameters:
        last_order_id: ID of the last successfully processed order.
        batch_size: Maximum number of records to extract.

    Returns:
        A list of dictionaries containing order records.
    """

    query = """
        SELECT
            order_id,
            customer_id,
            product_name,
            quantity,
            price,
            order_status,
            order_timestamp
        FROM orders
        WHERE order_id > %s
        ORDER BY order_id
        LIMIT %s;
    """

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (last_order_id, batch_size)
            )

            rows = cursor.fetchall()

            orders = []

            for row in rows:
                orders.append({
                    "order_id": row[0],
                    "customer_id": row[1],
                    "product_name": row[2],
                    "quantity": row[3],
                    "price": row[4],
                    "order_status": row[5],
                    "order_timestamp": row[6]
                })

            return orders

    except Exception as error:
        print("Extraction error:", error)
        return []

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":

    last_order_id = 0

    orders = extract_new_orders(
        last_order_id=last_order_id,
        batch_size=500
    )

    print(f"Extracted {len(orders)} order(s)")

    for order in orders:
        print(order)