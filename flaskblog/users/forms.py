from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired

class MessageForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Send')
