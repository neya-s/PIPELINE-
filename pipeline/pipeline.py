import time

# TODO: replace these with the real imports once extract.py and load.py are merged
# from extract import get_new_orders
# from load import insert_records

def run_pipeline():
    while True:
        new_orders = get_new_orders()          # gets new rows from orders table
        if new_orders:
            insert_records(new_orders)          # inserts them into orders_history
            print(f"Loaded {len(new_orders)} records")
        else:
            print("No new records")
        time.sleep(3)   # wait 3 seconds before checking again

if __name__ == "__main__":
    run_pipeline()
