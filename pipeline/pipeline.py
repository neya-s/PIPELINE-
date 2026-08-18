import time
from extract import extract_new_orders
from load import load_records

# Simple checkpoint file to remember the last processed order_id,
# so if the pipeline restarts, it doesn't reprocess or skip records.
CHECKPOINT_FILE = "last_order_id.txt"

def get_last_order_id():
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_last_order_id(order_id):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(order_id))

def run_pipeline(poll_interval=3, batch_size=500):
    last_order_id = get_last_order_id()
    total_processed = 0

    print(f"Starting pipeline. Resuming from order_id > {last_order_id}")

    while True:
        start_time = time.time()

        # 1. EXTRACT
        new_orders = extract_new_orders(last_order_id=last_order_id, batch_size=batch_size)

        if new_orders:
            # Fix the key name mismatch: extract.py uses "order_timestamp",
            # load.py expects "timestamp"
            for order in new_orders:
                order["timestamp"] = order.pop("order_timestamp")

            # 2. LOAD
            result = load_records(new_orders)

            if result["success"]:
                last_order_id = new_orders[-1]["order_id"]  # advance checkpoint
                save_last_order_id(last_order_id)
                total_processed += result["inserted"]

                elapsed = time.time() - start_time
                print(f"Loaded {result['inserted']} record(s) | "
                      f"Checkpoint now at order_id {last_order_id} | "
                      f"Took {elapsed:.2f}s | Total so far: {total_processed}")
            else:
                print(f"Load failed: {result['error']}")
        else:
            print("No new records.")

        time.sleep(poll_interval)

if __name__ == "__main__":
    run_pipeline(poll_interval=3, batch_size=500)
