from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, Booking
from app.forms import RegistrationForm, LoginForm, ProductForm, BookingForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            password=form.password.data,
            city=form.city.data,
            birth_date=form.birth_date.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone=form.phone.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный номер телефона или пароль', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('main.index'))

@main.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            quantity=form.quantity.data,
            location=form.location.data,
            price_per_day=form.price_per_day.data,
            history=form.history.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Товар успешно добавлен!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_product.html', form=form)

@main.route('/book_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def book_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(
            user_id=current_user.id,
            product_id=product.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(booking)
        db.session.commit()
        flash('Товар успешно забронирован!', 'success')
        return redirect(url_for('main.index'))
    return render_template('book_product.html', form=form, product=product)

@main.route('/track_delivery/<int:booking_id>')
@login_required
def track_delivery(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('track_delivery.html', booking=booking)