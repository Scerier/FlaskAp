from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from db import Users
import re
class LoginForm(FlaskForm):
    login = StringField("Login: ", validators=[DataRequired(),
                                                Length(min=4, max=20, message="Логин должен быть от 4 до 20 символов")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти", render_kw={'class': 'login_button'})
class RegisterForm(FlaskForm):
    login = StringField("Логин: ", validators=[Length(min=4, max=20, message="Логин должен быть от 4 до 20 символов")])
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    recaptcha = RecaptchaField()
    submit = SubmitField("Регистрация", render_kw={'class': 'login_button'})
    def validate_login(self, field):
        # Проверка на уникальность логина
        if Users.query.filter_by(login=field.data).first():
            raise ValidationError("Пользователь с таким логином уже зарегистрирован.")

        # Проверка на допустимые символы
        if not re.match(r'^[a-zA-Z0-9_]+$', field.data):
            raise ValidationError("Логин может содержать только латинские буквы, цифры и символ подчеркивания (_).")
    def validate_email(self, field):
        # Проверка на уникальность почты
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован.")