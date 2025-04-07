from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import (create_database, get_db_connection, add_user, get_all_products, send_message, get_messages,
                     add_product_status, get_product_status, get_orders, add_product, get_all_users, get_user_spending,
                     get_favorites, add_to_favorites, remove_from_favorites, get_spending_by_category)
import random
import string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

create_database()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8])
    return None

class User:
    def __init__(self, id, first_name, last_name, phone, password, city, birth_date, achievements, avatar_url):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.password = password
        self.city = city
        self.birth_date = birth_date
        self.achievements = achievements
        self.avatar_url = avatar_url

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

def generate_tracking_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@app.route('/')
def index():
    if current_user.is_authenticated:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM product_status WHERE user_id = ?', (current_user.id,))
        order_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM Messages WHERE receiver_id = ?', (current_user.id,))
        message_count = cursor.fetchone()[0]
        total_spent = get_user_spending(current_user.id)
        cursor.execute('SELECT COUNT(*) FROM products WHERE owner_id = ?', (current_user.id,))
        owned_products = cursor.fetchone()[0]
        spending_by_category = get_spending_by_category(current_user.id)
        conn.close()
        print(f"Index - Spending by category: {spending_by_category}")  # Отладка перед рендерингом
        return render_template('index.html', order_count=order_count, message_count=message_count, total_spent=total_spent,
                             owned_products=owned_products, spending_by_category=spending_by_category)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
        user = cursor.fetchone()
        conn.close()
        if user and user[4] == password:
            user_obj = User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8])
            login_user(user_obj)
            return redirect(url_for('index'))
        return "Неверный телефон или пароль"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        password = request.form['password']
        city = request.form['city']
        birth_date = request.form['birth_date']
        add_user(first_name, last_name, phone, password, city, birth_date)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    total_spent = get_user_spending(current_user.id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM product_status WHERE user_id = ?', (current_user.id,))
    order_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM products WHERE owner_id = ?', (current_user.id,))
    owned_products = cursor.fetchone()[0]
    spending_by_category = get_spending_by_category(current_user.id)
    conn.close()
    print(f"Profile - Spending by category: {spending_by_category}")  # Отладка перед рендерингом
    return render_template('profile.html', total_spent=total_spent, order_count=order_count, owned_products=owned_products,
                          spending_by_category=spending_by_category)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product_route():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        location = request.form['location']
        price_per_day = float(request.form['price_per_day'])
        history = request.form.get('history', '')
        description = request.form.get('description', '')
        latitude = float(request.form['latitude']) if request.form.get('latitude') else None
        longitude = float(request.form['longitude']) if request.form.get('longitude') else None
        image_url = request.form.get('image_url') or "https://images.unsplash.com/photo-1481349518771-20055b2a7b24"
        add_product(name, quantity, location, price_per_day, history, description, latitude, longitude, image_url, current_user.id)
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/messages')
@login_required
def messages():
    messages = get_messages(current_user.id)
    users = get_all_users()
    products = get_all_products()
    return render_template('messages.html', messages=messages, users=users, products=products)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message_route():
    receiver_id = request.form['receiver_id']
    product_id = request.form.get('product_id') or None
    message = request.form['message']
    send_message(current_user.id, receiver_id, product_id, message)
    return redirect('/messages')

@app.route('/products')
@login_required
def products():
    products = get_all_products()
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>')
@login_required
def product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    cursor.execute('SELECT first_name, last_name, avatar_url FROM users WHERE id = ?', (product[10],))
    owner = cursor.fetchone()
    cursor.execute('SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?', (current_user.id, product_id))
    is_favorite = bool(cursor.fetchone())
    conn.close()
    if not product:
        return "Товар не найден", 404
    return render_template('product.html', product=product, owner=owner, is_favorite=is_favorite)

@app.route('/use_card/<int:product_id>')
@login_required
def use_card(product_id):
    add_product_status(product_id, "Used", current_user.id)
    return redirect('/history')

@app.route('/history')
@login_required
def history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_status.*, products.name, products.image_url
        FROM product_status
        JOIN products ON product_status.product_id = products.id
        WHERE product_status.user_id = ?
        ORDER BY product_status.timestamp DESC
    ''', (current_user.id,))
    statuses = cursor.fetchall()
    conn.close()
    return render_template('history.html', statuses=statuses)

@app.route('/orders')
@login_required
def orders():
    orders = get_orders(current_user.id)
    return render_template('orders.html', orders=orders)

@app.route('/create_order/<int:product_id>', methods=['POST'])
@login_required
def create_order(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT price_per_day FROM products WHERE id = ?', (product_id,))
    price_per_day = cursor.fetchone()[0]
    cost = price_per_day * random.uniform(1, 30)
    tracking_number = generate_tracking_number()
    add_product_status(product_id, "In Transit", current_user.id, tracking_number, cost)
    conn.close()
    return redirect('/orders')

@app.route('/update_order/<int:order_id>/<string:status>')
@login_required
def update_order(order_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE product_status SET status = ? WHERE id = ? AND user_id = ?', (status, order_id, current_user.id))
    conn.commit()
    conn.close()
    return redirect('/orders')

@app.route('/favorites')
@login_required
def favorites():
    favorites = get_favorites(current_user.id)
    return render_template('favorites.html', favorites=favorites)

@app.route('/add_to_favorites/<int:product_id>')
@login_required
def add_to_favorites_route(product_id):
    add_to_favorites(current_user.id, product_id)
    return redirect(url_for('product', product_id=product_id))

@app.route('/remove_from_favorites/<int:product_id>')
@login_required
def remove_from_favorites_route(product_id):
    remove_from_favorites(current_user.id, product_id)
    return redirect(url_for('product', product_id=product_id))

if __name__ == '__main__':
    app.run(debug=True)