from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

username_regex = r'^(?=.{5,}$)(?=.*[a-z])(?=.*[A-Z]).+$'
password_regex = r'^(?=.{5,}$)(?=.*[A-Za-z])(?=.*\d)(?=.*[$%*@]).+$'

class RegistrationForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(),
                    Length(min=5),
                    Regexp(username_regex,
                           message="Username must have at least 5 chars with both upper and lower case letters.")])
    password = PasswordField('Password',
        validators=[DataRequired(),
                    Regexp(password_regex,
                           message="Password must have a letter, a digit, and one of $, %, *, @")])
    confirm = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
