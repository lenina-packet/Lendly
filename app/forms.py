from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    phone = StringField('Номер телефона', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ProductForm(FlaskForm):
    name = StringField('Наименование товара', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired()])
    location = StringField('Местоположение', validators=[DataRequired()])
    price_per_day = FloatField('Цена за сутки аренды', validators=[DataRequired()])
    history = TextAreaField('История городов')
    submit = SubmitField('Добавить товар')

class BookingForm(FlaskForm):
    start_date = DateField('Дата начала аренды', validators=[DataRequired()])
    end_date = DateField('Дата окончания аренды', validators=[DataRequired()])
    submit = SubmitField('Забронировать')