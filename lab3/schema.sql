PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    price REAL NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'paid', 'shipped', 'completed', 'cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

CREATE VIEW product_catalog AS
SELECT
    p.id,
    p.name AS product,
    c.name AS category,
    p.sku,
    p.price,
    p.stock_quantity
FROM products AS p
JOIN categories AS c ON c.id = p.category_id;

CREATE VIEW order_totals AS
SELECT
    o.id AS order_id,
    c.full_name AS customer,
    o.created_at,
    o.status,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total
FROM orders AS o
JOIN customers AS c ON c.id = o.customer_id
JOIN order_items AS oi ON oi.order_id = o.id
GROUP BY o.id, c.full_name, o.created_at, o.status;

CREATE TRIGGER validate_order_item_price
BEFORE INSERT ON order_items
WHEN NEW.unit_price <= 0
BEGIN
    SELECT RAISE(ABORT, 'Unit price must be greater than zero');
END;

INSERT INTO categories (name, description) VALUES
    ('Электроника', 'Гаджеты и электронные устройства'),
    ('Дом и кухня', 'Товары для дома'),
    ('Книги', 'Художественная и учебная литература'),
    ('Спорт', 'Спортивные товары и аксессуары');

INSERT INTO products (category_id, name, sku, price, stock_quantity) VALUES
    (1, 'Беспроводные наушники', 'EL-HEAD-001', 5490.00, 18),
    (1, 'Портативная колонка', 'EL-SPKR-002', 3990.00, 11),
    (1, 'Внешний аккумулятор', 'EL-PWR-003', 2490.00, 25),
    (2, 'Электрический чайник', 'HM-KETT-001', 2890.00, 9),
    (2, 'Настольная лампа', 'HM-LAMP-002', 1790.00, 14),
    (3, 'Проектирование интерфейсов', 'BK-GUI-002', 1680.00, 8),
    (4, 'Коврик для йоги', 'SP-YOGA-001', 1590.00, 16),
    (4, 'Набор гантелей', 'SP-DUMB-002', 4290.00, 6);

INSERT INTO customers (full_name, email, phone) VALUES
    ('Анна Соколова', 'anna@example.com', '+7 927 100-20-30'),
    ('Иван Петров', 'ivan@example.com', '+7 927 200-30-40'),
    ('Мария Волкова', 'maria@example.com', '+7 927 300-40-50'),
    ('Алексей Орлов', 'alexey@example.com', '+7 927 400-50-60');

INSERT INTO orders (customer_id, created_at, status) VALUES
    (1, '2026-09-18 10:15:00', 'completed'),
    (2, '2026-09-22 16:40:00', 'shipped'),
    (1, '2026-10-03 12:05:00', 'paid'),
    (3, '2026-10-08 09:30:00', 'new'),
    (4, '2026-10-10 18:20:00', 'cancelled');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 5490.00),
    (1, 3, 2, 2490.00),
    (2, 4, 1, 2890.00),
    (2, 5, 2, 1790.00),
    (3, 6, 1, 1350.00),
    (3, 7, 1, 1680.00),
    (4, 8, 2, 1590.00),
    (5, 2, 1, 3990.00);
