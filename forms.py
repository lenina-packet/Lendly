from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class ProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired()])
    location = StringField('Местоположение', validators=[DataRequired()])
    price_per_day = FloatField('Цена за сутки аренды', validators=[DataRequired()])
    history = TextAreaField('История городов')
    description = TextAreaField('Описание товара', validators=[DataRequired()])  # Убедитесь, что это поле есть
    submit = SubmitField('Добавить товар')

class LoginForm(FlaskForm):
    phone = StringField('Номер телефона', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')