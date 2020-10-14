from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import BooleanField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                    validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                    validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                    validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password',
                    validators=[DataRequired(), EqualTo('password')])
    image = FileField('Set Profile Image', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                    validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                    validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                    validators=[DataRequired(), Email()])
    submit = SubmitField('Request')

class ResetForm(FlaskForm):
    password = PasswordField('Password',
                    validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password',
                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')
