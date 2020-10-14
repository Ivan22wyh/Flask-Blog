from datetime import date
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Account, Post
from flaskblog.blog.forms import PostForm

posts = Blueprint('posts', __name__)

day = str(date.today())

@posts.route('/blog', methods=['GET', 'POST'])
def blog():
	order = request.args.get('order', 'desc', str )
	page = request.args.get('page', 1, type=int)
	if order == 'desc':
		posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=5)
	elif order == 'asc':
		posts = Post.query.paginate(page=page, per_page=5)
	return render_template('/blog/blog.html', title='Post', posts=posts)

@posts.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(
			title=form.title.data,
			content=form.content.data,
			date_posted=day
		)
		current_user.posts.append(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('posts.blog'))
	return render_template('/blog/new_post.html', title='New Post', form=form)

@posts.route('/post/<int:post_id>', methods=['GET', 'POST'])
def the_post(post_id):
	post = Post.query.get(post_id)
	return render_template('/blog/the_post.html', title=post.title, post=post)

@posts.route('/updatepost/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get(post_id)
	if post.account.email != current_user.email:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('posts.the_post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('/blog/update_post.html', title='Update Post', post=post, form=form)

@posts.route('/deletepost/<int:post_id>')
@login_required
def delete_post(post_id):
	post = Post.query.get(post_id)
	if post.account.email != current_user.email:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted.', 'info')
	return redirect(url_for('posts.blog'))

@posts.route('/starpost/<int:post_id>')
@login_required
def star_post(post_id):
	post = Post.query.get(post_id)
	if post not in current_user.stars:
		current_user.stars.append(post)
	db.session.commit()
	flash("Star post successfully", 'success')
	return redirect(url_for('posts.the_post', post_id=post.id))

@posts.route('/unstarpost/<int:post_id>')
@login_required
def unstar_post(post_id):
	post = Post.query.get(post_id)
	if post in current_user.stars:
		current_user.stars.remove(post)
	db.session.commit()
	flash("Unstar post successfully", 'info')
	return redirect(url_for('posts.the_post', post_id=post.id))
