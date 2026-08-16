INSERT INTO orders
    (customer_id, product_name, quantity, price, order_status, order_timestamp)
VALUES
    (101, 'Laptop', 1, 55000.00, 'Completed', CURRENT_TIMESTAMP),
    (102, 'Wireless Mouse', 2, 1200.00, 'Pending', CURRENT_TIMESTAMP),
    (103, 'Keyboard', 1, 2500.00, 'Shipped', CURRENT_TIMESTAMP),
    (104, 'Headphones', 3, 3500.00, 'Completed', CURRENT_TIMESTAMP),
    (105, 'Monitor', 1, 15000.00, 'Pending', CURRENT_TIMESTAMP);