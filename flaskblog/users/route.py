from sqlalchemy import or_, and_
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Account, Post, Message
from flaskblog.users.forms import MessageForm

users = Blueprint('users', __name__)

@users.route('/<int:id>/posts', methods=['GET', 'POST'])
def user_posts(id):
	page = request.args.get('page', 1, type=int)
	user = Account.query.filter_by(id=id).first()
	posts = Post.query.order_by(Post.id.desc()).filter_by(account_id=user.id).paginate(page=page, per_page=5)	
	form = MessageForm()
	if form.validate_on_submit():
		message = Message(
			content=form.content.data,
			timestamp=datetime.today()
		)
		user.messages_recieved.append(message)
		current_user.messages_sent.append(message)
		db.session.commit()
		flash('Your messages has been sended successfully', 'success')
		return redirect(url_for('users.user_posts', id=user.id))
	if current_user.is_authenticated:
		if user.id == current_user.id:
			return redirect(url_for('current.account_posts'))
	image_file = url_for('static', filename='images/profile_img/'+user.img)
	return render_template('/user/user_posts.html',user=user, title='User', subtitle='User_Post',
						img_file=image_file, posts=posts, form=form)

@users.route('/<int:id>/following', methods=['GET', 'POST'])
def user_following(id):
	page = request.args.get('page', 1, type=int)
	user = Account.query.filter_by(id=id).first()
	following_id = [x.id for x in user.followings]
	following_paginate = Account.query.filter(Account.id.in_(following_id)).paginate(page=page, per_page=10)
	form = MessageForm()
	if form.validate_on_submit():
		message = Message(
			content=form.content.data,
			timestamp=datetime.today()
		)
		user.messages_recieved.append(message)
		current_user.messages_sent.append(message)
		db.session.commit()
		flash('Your messages has been sended successfully', 'success')
		return redirect(url_for('users.user_following', id=user.id))
	if current_user.is_authenticated:
		if user.id == current_user.id:
			return redirect(url_for('current.account_posts'))
	image_file = url_for('static', filename='images/profile_img/'+user.img)
	return render_template('/user/user_following.html',user=user, title='User', subtitle='User_Following',
						img_file=image_file, followings=following_paginate, form=form)

@users.route('/<int:id>/followers', methods=['GET', 'POST'])
def user_followers(id):
	page = request.args.get('page', 1, type=int)
	user = Account.query.filter_by(id=id).first()
	follower_id = [x.id for x in user.followers]
	follower_paginate = Account.query.filter(Account.id.in_(follower_id)).paginate(page=page, per_page=10)
	form = MessageForm()
	if form.validate_on_submit():
		message = Message(
			content=form.content.data,
			timestamp=datetime.today()
		)
		user.messages_recieved.append(message)
		current_user.messages_sent.append(message)
		db.session.commit()
		flash('Your messages has been sended successfully', 'success')
		return redirect(url_for('users.user_followers', id=user.id))
	if current_user.is_authenticated:
		if user.id == current_user.id:
			return redirect(url_for('current.account_posts'))
	image_file = url_for('static', filename='images/profile_img/'+user.img)
	return render_template('/user/user_followers.html',user=user, title='User', subtitle='User_Follower',
						img_file=image_file, followers=follower_paginate, form=form)

@users.route('/<int:id>/stars', methods=['GET', 'POST'])
def user_favorities(id):
	page = request.args.get('page', 1, type=int)
	user = Account.query.filter_by(id=id).first()
	star_id = [x.id for x in user.stars]
	star_paginate = Post.query.order_by(Post.id.desc()).filter(Post.id.in_(star_id)).paginate(page=page, per_page=5)
	form = MessageForm()
	if form.validate_on_submit():
		message = Message(
			content=form.content.data,
			timestamp=datetime.today()
		)
		user.messages_recieved.append(message)
		current_user.messages_sent.append(message)
		db.session.commit()
		flash('Your messages has been sended successfully', 'success')
		return redirect(url_for('users.user_favorities', id=user.id))
	if current_user.is_authenticated:
		if user.id == current_user.id:
			return redirect(url_for('current.account_stars'))
	posts = user.stars
	image_file = url_for('static', filename='images/profile_img/'+user.img)
	return render_template('/user/user_stars.html',user=user, title='User', subtitle='User_Star',
						img_file=image_file, posts=star_paginate, form=form)

@users.route('/<int:user_id>/messages', methods=['GET', 'POST'])
@login_required
def user_message(user_id):
	form = MessageForm()
	user = Account.query.get(user_id)
	page = request.args.get('page', 1, type=int)
	image_file = url_for('static', filename='images/profile_img/'+user.img)
	message_filter = {
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
	messages = Message.query.order_by(Message.id.desc()).filter(*message_filter).paginate(page=page, per_page=10)
	if form.validate_on_submit():
		message = Message(
			content=form.content.data,
			timestamp=datetime.today()
		)
		user.messages_recieved.append(message)
		current_user.messages_sent.append(message)
		db.session.commit()
		flash('Your messages has been sended successfully', 'success')
		return redirect(url_for('users.user_message', user_id=user.id))
	return render_template('/user/user_message.html', user=user, title='User', subtitle='User_Message',
						img_file=image_file, messages=messages, form=form, Account=Account)

@users.route('/follow/<int:account_id>')
@login_required
def follow(account_id):
	account = Account.query.get(account_id)
	if account not in current_user.followings:
		current_user.followings.append(account)
	db.session.commit()
	flash('Follow this user successfully', 'success')
	return redirect(url_for('users.user_posts', id=account.id))

@users.route('/not_follow/<int:account_id>')
@login_required
def not_follow(account_id):
	account = Account.query.get(account_id)
	if account in current_user.followings:
		current_user.followings.remove(account)
	db.session.commit()
	flash('Already not to follow this user', 'info')
	return redirect(url_for('users.user_posts', id=account.id))
