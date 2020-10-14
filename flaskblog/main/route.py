from time import sleep
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog import bcrypt, mail, db
from flaskblog.models import Account
from flaskblog.main.forms import LoginForm, RequestResetForm, ResetForm, RegistrationForm
from flaskblog.main.utils import save_image, send_reset_email

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
	return render_template('/main/home.html', title='Home')

@main.route('/about')
def about():
	abort(403)
	return render_template('/main/about.html', title='about')

@main.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		if form.image.data:
			img_file = save_image(form.image.data)
		else:
			img_file = 'default_1.jpg'
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		new_account = Account(
			username = form.username.data,
			email = form.email.data,
			password = hashed_password,
			img = img_file
		)
		try:
			if Account.query.filter_by(email=form.email.data).first():
				flash('The email address is already existed, please change another.', 'danger')
			elif Account.query.filter_by(username=form.username.data).first():
				flash('The username is already existed, please change another.', 'danger')
			else:
				db.session.add(new_account)
				db.session.commit()
				sleep(1)
				return redirect(url_for('main.login'))
		except:
			raise
	return render_template('/main/register.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		account = Account.query.filter_by(email=form.email.data).first()
		try:
			if current_user.is_authenticated:
				flash("The account has been signed in, there's no need to sign in again.", 'success')
			elif bcrypt.check_password_hash(account.password, form.password.data):
				login_user(account)
				next_page = request.args.get('next')
				return redirect(next_page) if next_page else redirect(url_for('main.home'))
			elif account:
				flash('Sign in Unsuccessful. Please check your e-mail and password again.', 'danger')
			else:
				flash('Some issues had occured. Please check your e-mail and password again.', 'danger')
		except:
			flash('The account is not existed. Please check your e-mail and password again.', 'danger')
	return render_template('/main/login.html', title='Login', form=form)

@main.route('/reset', methods=['GET', 'POST'])
def reset():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	token = request.args.get('token', '', str)
	if token == '':
		form = RequestResetForm()
		if form.validate_on_submit():
			user = Account.query.filter_by(email=form.email.data).first()
			send_reset_email(user)
		return render_template('/main/reset.html', title='Request Reset', form=form)
	elif token:
		form = ResetForm()
		user = Account.verify_reset_token(token)
		if user is None:
			flash('That is an invalid or expired token', 'warning')
			return redirect(url_for('main.reset'))
		if form.validate_on_submit():
			hashed_password = bcrypt.generate_password_hash(form.password.data)
			user.password = hashed_password
			db.session.commit()
			flash('Your password has been reset successfully.', 'info')
			return redirect(url_for('main.login'))
		return render_template('/main/reset.html', title='Reset', form=form)


@main.route('/logout', methods=['GET', 'POST'])
def logout():
	logout_user()
	return redirect(url_for('main.home'))

