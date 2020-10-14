import os
from secrets import token_hex
from PIL import Image
from flask import url_for, flash, current_app
from flask_mail import Message
from flaskblog import mail
from flaskblog.main.forms import RegistrationForm, LoginForm, ResetForm, RequestResetForm


def save_image(form_image):
	random_hex = token_hex(8)
	_, f_ext = os.path.splitext(form_image.filename)
	img_fn = random_hex + f_ext
	img_path = os.path.join(current_app.root_path, 'static/images/profile_img', img_fn)
	
	output_size = (125, 125)
	i= Image.open(form_image)
	i.thumbnail(output_size)
	i.save(img_path)

def send_reset_email(user):
	if user is None:
		flash("There's no account with that email, please create one first.", 'warning')
		return
	else:
		token = user.get_reset_token()
		msg = Message('Password Reset Request', 
					sender='Ivan22wyh@outlook.com', 
					recipients=[user.email])
		msg.body = f'''To reset your password, visit the following link:
{url_for('main.reset', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
		mail.send(msg)
		flash('An email has been sent with instructions to reset your password', 'info')
		return