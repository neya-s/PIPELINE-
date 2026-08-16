"""
load.py - Load Module (Team Member 4)

Receives extracted order records (list of dicts, as produced by
extract.py's extract_new_orders()) and inserts them into orders_history.

Contract with Extract module (Team Member 3):
- Input: list of dicts, each with all 7 columns from `orders`
  (order_id, customer_id, product_name, quantity, price, order_status, timestamp)
- Records are inserted EXACTLY as received - no transformations.
- orders_history.order_id is the PRIMARY KEY, so duplicates are handled
  with ON CONFLICT (order_id) DO NOTHING.
- This module does NOT manage the checkpoint. It only reports how many
  rows were actually inserted so pipeline.py can decide whether to
  advance the checkpoint (only after a successful load).
"""

import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "dbname": "orders_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}

INSERT_QUERY = """
    INSERT INTO orders_history (
        order_id, customer_id, product_name, quantity, price, order_status, timestamp
    )
    VALUES %s
    ON CONFLICT (order_id) DO NOTHING;
"""


def get_connection():
    """Create and return a new PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)


def load_records(records, conn=None):
    """
    Insert a list of order dicts into orders_history.

    Args:
        records (list[dict]): records from extract_new_orders(), each with
            keys: order_id, customer_id, product_name, quantity, price,
            order_status, timestamp.
        conn: optional existing psycopg2 connection. If not provided,
            a new one is opened and closed within this function.

    Returns:
        dict: {
            "success": bool,
            "attempted": int,   # number of records passed in
            "inserted": int,    # number of rows actually inserted
                                 # (excludes ON CONFLICT skips)
            "error": str | None
        }
    """
    result = {"success": False, "attempted": len(records), "inserted": 0, "error": None}

    if not records:
        result["success"] = True
        return result

    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    try:
        # Preserve record order and structure exactly as received.
        values = [
            (
                r["order_id"],
                r["customer_id"],
                r["product_name"],
                r["quantity"],
                r["price"],
                r["order_status"],
                r["timestamp"],
            )
            for r in records
        ]

        with conn.cursor() as cur:
            # execute_values gives fast multi-row insert in one round trip.
            psycopg2.extras.execute_values(cur, INSERT_QUERY, values)
            # rowcount after ON CONFLICT DO NOTHING reflects only the rows
            # that were actually inserted (skipped duplicates don't count).
            result["inserted"] = cur.rowcount

        conn.commit()
        result["success"] = True

    except Exception as e:
        conn.rollback()
        result["error"] = str(e)
        result["success"] = False

    finally:
        if own_conn:
            conn.close()

    return result


if __name__ == "__main__":
    # Quick manual test with dummy records matching Team Member 3's structure
    sample_records = [
        {
            "order_id": 1,
            "customer_id": 101,
            "product_name": "Test Product",
            "quantity": 2,
            "price": 499.00,
            "order_status": "PLACED",
            "timestamp": "2026-08-16 10:00:00",
        }
    ]
    outcome = load_records(sample_records)
    print(outcome)