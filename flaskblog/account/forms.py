from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                    validators=[Length(min=2, max=20)])
    email = StringField('Email', 
                    validators=[Email()])
    image = FileField('Update Profile Image', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')  

class MessageForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Send')