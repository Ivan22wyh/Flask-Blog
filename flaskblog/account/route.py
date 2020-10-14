import os
from secrets import token_hex
from datetime import datetime
from PIL import Image
from flask import Blueprint, render_template, redirect, request, url_for, flash, Blueprint
from flask_login import logout_user, current_user, login_required
from sqlalchemy import or_, and_
from flaskblog import db
from flaskblog.models import Account, Post, Message  
from flaskblog.account.forms import MessageForm, UpdateAccountForm
from flaskblog.account.utils import save_image

current = Blueprint('current', __name__)

@current.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	print(os.environ.get('FLASKBLOG_SECRET_KEY'))
	form = UpdateAccountForm()
	image_file = url_for('static', filename='images/profile_img/'+current_user.img)
	if form.validate_on_submit():
		try:
			if form.image.data:
				current_user.img = save_image(form.image.data)			
			if (Account.query.filter_by(email=form.email.data).first() == None or current_user.email == form.email.data)\
					 and (Account.query.filter_by(username=form.username.data).first() == None or current_user.username == form.username.data):
				current_user.username = form.username.data
				current_user.email = form.email.data
				db.session.commit()
				logout_user()
				return redirect(url_for('current.account'))
			else:
				flash('The email has been registered, please change it.', 'info')
			return redirect(url_for('current.account'))
		except:
			raise
			flash('Some issues had occured when updating your account info, please try again later.', 'danger')
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('/account/account.html', title='Account', subtitle='Account',
						img_file=image_file, form=form)

@current.route('/account/posts', methods=['GET', 'POST'])
@login_required
def account_posts():
	page = request.args.get('page', 1, type=int)
	image_file = url_for('static', filename='images/profile_img/'+current_user.img)
	posts = Post.query.order_by(Post.id.desc()).filter_by(account_id=current_user.id).paginate(page=page, per_page=5)
	return render_template('/account/account_posts.html', title='Account', subtitle='Account_Post',
						img_file=image_file, posts=posts)

@current.route('/account/followers', methods=['GET', 'POST'])
@login_required
def account_followers():
	page = request.args.get('page', 1, type=int)
	follower_id = [x.id for x in current_user.followers]
	follower_paginate = Account.query.filter(Account.id.in_(follower_id)).paginate(page=page, per_page=10)
	image_file = url_for('static', filename='images/profile_img/'+current_user.img)
	return render_template('/account/account_followers.html', title='Account', subtitle='Account_Follower',
						img_file=image_file, followers = follower_paginate)

@current.route('/account/following', methods=['GET', 'POST'])
@login_required
def account_following():
	page = request.args.get('page', 1, type=int)
	image_file = url_for('static', filename='images/profile_img/'+current_user.img)
	following_id = [x.id for x in current_user.followings]
	following_paginate = Account.query.filter(Account.id.in_(following_id)).paginate(page=page, per_page=10)  
	return render_template('/account/account_following.html', title='Account', subtitle='Account_Following',
						img_file=image_file, followings=following_paginate)

@current.route('/account/stars', methods=['GET', 'POST'])
@login_required
def account_stars():
	page = request.args.get('page', 1, type=int)
	star_id = [x.id for x in current_user.stars]
	star_paginate = Post.query.order_by(Post.id.desc()).filter(Post.id.in_(star_id)).paginate(page=page, per_page=5)
	image_file = url_for('static', filename='images/profile_img/'+current_user.img)
	return render_template('/account/account_stars.html', title='Account', subtitle='Account_Star', 
						img_file=image_file, posts=star_paginate)

@current.route('/account/messages', methods=['GET', 'POST', 'PUT'])
@login_required
def account_messages():
	mate = request.args.get('user', '', type=str)
	page = request.args.get('page', 1, type=int)
	current_user.last_message_read_time = datetime.today()
	db.session.commit()
	if mate == '':
		image_file = url_for('static', filename='images/profile_img/'+current_user.img)
		messages = Message.query.filter(or_(Message.sender_id==current_user.id, Message.recipient_id==current_user.id)).all()
		users = []
		for message in messages:
			if message.sender_id == current_user.id and message.recipient_id not in users:
				users.append(message.recipient_id)
			elif message.recipient_id == current_user.id and message.sender_id not in users:
				users.append(message.sender_id)
		return render_template('/account/account_messages.html', title='Account', subtitle='Account_Message',
							img_file=image_file, users=users, Message=Message, Account=Account)
	else:
		user = Account.query.filter_by(username=mate).first()
		form = MessageForm()
		chat_message_filter = {
			or_(
				and_(
				Message.sender_id==current_user.id,
				Message.recipient_id==user.id
			),
				and_(
				Message.sender_id==user.id,
				Message.recipient_id==current_user.id
			)
			)
		}
		image_file = url_for('static', filename='images/profile_img/'+user.img) 
		messages = Message.query.order_by(Message.id.desc()).filter(*chat_message_filter).paginate(page=page, per_page=5)
		if form.validate_on_submit():
			message = Message(
				content=form.content.data,
				timestamp=datetime.today()
			)
			current_user.messages_sent.append(message)
			user.messages_recieved.append(message)
			db.session.commit()
			flash('Your messages has been sended successfully', 'success')
			return redirect(url_for('current.account_messages', user=user.username))
		return render_template('/account/account_chat.html', user=user, messages=messages, img_file=image_file,
						Account=Account, form=form)

@current.route('/delete_message/<int:user_id>', methods=['GET','POST'])
@login_required
def delete_message(user_id):
	user = Account.query.get(user_id)
	message_delete_filter = {
		or_(
			and_(
				Message.sender_id == current_user.id,
				Message.recipient_id == user.id
			),
			and_(
				Message.sender_id == user.id,
				Message.recipient_id == current_user.id
			)
		)
	}
	messages = Message.query.filter(*message_delete_filter).all()
	for message in messages:
		db.session.delete(message)
		db.session.commit()
	flash('Your message has been deleted successfully', 'info')
	return redirect(url_for('current.account_messages'))