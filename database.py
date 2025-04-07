import sqlite3
import os
from faker import Faker
import random
import string

DATABASE_PATH = 'lendly.db'

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def create_database():
    if not os.path.exists(DATABASE_PATH):
        print("База данных не найдена. Создаем новую...")
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                city TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                achievements TEXT,
                avatar_url TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                location TEXT NOT NULL,
                price_per_day REAL NOT NULL,
                history TEXT,
                description TEXT,
                latitude REAL,
                longitude REAL,
                image_url TEXT,
                owner_id INTEGER,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                product_id INTEGER,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                user_id INTEGER,
                tracking_number TEXT,
                cost REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        conn.commit()
        conn.close()
        print("База данных успешно создана.")
        populate_database()
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            populate_database()

def populate_database():
    fake = Faker('ru_RU')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Пользователи
    users = []
    achievements_list = [
        "Новичок (1 заказ)", "Активный участник (10 заказов)", "Мастер аренды (50 заказов)",
        "Щедрый арендодатель (10 товаров)", "Звезда платформы (100 сообщений)"
    ]
    for i in range(100):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.unique.phone_number()
        password = "password123"
        city = fake.city()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%Y-%m-%d')
        achievements = ",".join(random.sample(achievements_list, random.randint(0, 3)))
        avatar_url = f"https://ui-avatars.com/api/?name={first_name}+{last_name}&size=150"  # Аватары на основе имени
        cursor.execute('INSERT INTO users (first_name, last_name, phone, password, city, birth_date, achievements, avatar_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (first_name, last_name, phone, password, city, birth_date, achievements, avatar_url))
        users.append(cursor.lastrowid)
    conn.commit()

    # Товары
    cities = [
        ("Москва", 55.751244, 37.618423),
        ("Санкт-Петербург", 59.934280, 30.335098),
        ("Казань", 55.830431, 49.066081),
        ("Новосибирск", 55.008353, 82.935733),
        ("Екатеринбург", 56.838926, 60.605702),
    ]
    image_urls = [
        "https://images.unsplash.com/photo-1561037404-61cd46aa615b",  # Собака
        "https://images.unsplash.com/photo-1518791841217-8f162f1e1131",  # Кот
        "https://images.unsplash.com/photo-1481349518771-20055b2a7b24",  # Рандом
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",  # Пляж
        "https://images.unsplash.com/photo-1518655061710-4931d28f44f3",  # Велосипед
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",  # Наушники
        "https://images.unsplash.com/photo-1507146153580-69a1fe6d8aa1",  # Дрон
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",  # Телефон
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a0a6",  # Ноутбук
        "https://images.unsplash.com/photo-1523275339254-cc5c0e54c03e",  # Часы
    ]
    for i in range(200):
        name = f"{fake.word().capitalize()} {fake.word().capitalize()}"
        quantity = random.randint(1, 5)
        city, lat, lon = random.choice(cities)
        price_per_day = round(random.uniform(100, 5000), 2)
        history = fake.sentence()
        description = fake.paragraph()
        image_url = random.choice(image_urls)
        owner_id = random.choice(users)
        cursor.execute('INSERT INTO products (name, quantity, location, price_per_day, history, description, latitude, longitude, image_url, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (name, quantity, city, price_per_day, history, description, lat, lon, image_url, owner_id))
    conn.commit()

    # Заказы
    product_ids = [i for i in range(1, 201)]
    for _ in range(500):
        product_id = random.choice(product_ids)
        user_id = random.choice(users)
        status = random.choice(["In Transit", "Received", "Completed"])
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        cursor.execute('SELECT price_per_day FROM products WHERE id = ?', (product_id,))
        price_per_day = cursor.fetchone()[0]
        cost = round(price_per_day * random.uniform(1, 30), 2)
        cursor.execute('INSERT INTO product_status (product_id, status, user_id, tracking_number, cost) VALUES (?, ?, ?, ?, ?)',
                       (product_id, status, user_id, tracking_number, cost))
    conn.commit()

    # Сообщения
    for _ in range(1000):
        sender_id = random.choice(users)
        receiver_id = random.choice([u for u in users if u != sender_id])
        product_id = random.choice(product_ids + [None])
        message = fake.sentence()
        cursor.execute('INSERT INTO Messages (sender_id, receiver_id, product_id, message) VALUES (?, ?, ?, ?)',
                       (sender_id, receiver_id, product_id, message))
    conn.commit()

    # Избранное
    for user_id in random.sample(users, 50):
        favorite_products = random.sample(product_ids, random.randint(1, 10))
        for product_id in favorite_products:
            cursor.execute('INSERT INTO favorites (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    conn.commit()

    conn.close()
    print("База данных наполнена тестовыми данными.")

def add_user(first_name, last_name, phone, password, city, birth_date, achievements="", avatar_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    avatar_url = avatar_url or f"https://ui-avatars.com/api/?name={first_name}+{last_name}&size=150"
    cursor.execute('INSERT INTO users (first_name, last_name, phone, password, city, birth_date, achievements, avatar_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (first_name, last_name, phone, password, city, birth_date, achievements, avatar_url))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def add_product(name, quantity, location, price_per_day, history=None, description=None, latitude=None, longitude=None, image_url=None, owner_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, quantity, location, price_per_day, history, description, latitude, longitude, image_url, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (name, quantity, location, price_per_day, history, description, latitude, longitude, image_url, owner_id or None))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def send_message(sender_id, receiver_id, product_id, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Messages (sender_id, receiver_id, product_id, message) VALUES (?, ?, ?, ?)',
                   (sender_id, receiver_id, product_id, message))
    conn.commit()
    conn.close()

def get_messages(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Messages.*, users.first_name, users.last_name, users.avatar_url, products.name
        FROM Messages
        JOIN users ON Messages.sender_id = users.id
        LEFT JOIN products ON Messages.product_id = products.id
        WHERE (Messages.receiver_id = ? OR Messages.sender_id = ?)
        ORDER BY Messages.timestamp DESC
    ''', (user_id, user_id))
    messages = cursor.fetchall()
    conn.close()
    return messages

def add_product_status(product_id, status, user_id=None, tracking_number=None, cost=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO product_status (product_id, status, user_id, tracking_number, cost) VALUES (?, ?, ?, ?, ?)',
                   (product_id, status, user_id, tracking_number, cost))
    conn.commit()
    conn.close()

def get_product_status(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if product_id:
        cursor.execute('SELECT * FROM product_status WHERE product_id = ? ORDER BY timestamp DESC', (product_id,))
    else:
        cursor.execute('SELECT * FROM product_status ORDER BY timestamp DESC')
    statuses = cursor.fetchall()
    conn.close()
    return statuses

def get_orders(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT product_status.*, products.name FROM product_status JOIN products ON product_status.product_id = products.id WHERE product_status.user_id = ?', (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_user_spending(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(cost) FROM product_status WHERE user_id = ? AND cost IS NOT NULL', (user_id,))
    total_spent = cursor.fetchone()[0] or 0
    conn.close()
    return total_spent

def get_favorites(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT products.* FROM favorites JOIN products ON favorites.product_id = products.id WHERE favorites.user_id = ?', (user_id,))
    favorites = cursor.fetchall()
    conn.close()
    return favorites

def add_to_favorites(user_id, product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    conn.commit()
    conn.close()

def remove_from_favorites(user_id, product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM favorites WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    conn.commit()
    conn.close()

def get_spending_by_category(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.name, SUM(product_status.cost) as total_cost
        FROM product_status
        JOIN products ON product_status.product_id = products.id
        WHERE product_status.user_id = ? AND product_status.cost IS NOT NULL
        GROUP BY products.id, products.name
    ''', (user_id,))
    spending = cursor.fetchall()
    conn.close()
    print(f"User ID: {user_id}, Spending by category: {spending}")  # Отладка в консоль
    if not spending:
        print(f"No spending data found for user {user_id}")
        return [("Нет данных", 0)]
    return spending