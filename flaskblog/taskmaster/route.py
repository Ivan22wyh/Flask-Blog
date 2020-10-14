from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flaskblog import db
from flaskblog.models import Account, Task
from flask_login import current_user, login_required
from flaskblog.taskmaster.forms import TaskForm

tasks = Blueprint('tasks', __name__)

@tasks.route('/taskmaster', methods=['POST', 'GET'])
@login_required
def taskmaster():
	if request.method == 'POST':
		new_task = Task(
			content=request.form['content'],
			deadline = request.form['deadline'],
			completed='Not yet',
			completed_num=0,
			priority='Just Fine',
			priority_num=3
			)
		try:
			current_user.tasks.append(new_task)
			db.session.commit()
		except:
			return 'Some issues had occured, please check your web connection.'
		flash('Your task has been added successfully', 'success')
		return redirect('/taskmaster')
	else:
		page = request.args.get('page', 1, type=int)
		tasks = Task.query.order_by(Task.deadline, Task.priority_num).filter_by(account=current_user, completed_num=0)\
								.paginate(page=page, per_page=10)
		return render_template('/task/taskmaster.html', tasks=tasks, title='taskmaster')

@tasks.route('/taskmaster/delete/<int:id>')
@login_required
def delete(id):
	task = Task.query.filter_by(id=id).first()
	if task.account.email != current_user.email:
		abort(403)
	try:
		db.session.delete(task)
		db.session.begin_nested() # a kind of savepoint
		db.session.rollback() # all the transaction after commit or begin_nested will be canceled
		db.session.commit()
		flash('Your task has been deleted successfully', 'danger')
		return redirect('/taskmaster')
	except:
		return 'Some issues had occured, please check your web connection'

@tasks.route('/taskmaster/updatetask/<int:task_id>', methods=['POST', 'GET'])
@login_required
def updatetask(task_id):
	# the variable can pass into render_template
	form = TaskForm()
	task = Task.query.filter_by(id=task_id).first()
	if task.account.email != current_user.email:
		abort(403)
	if form.validate_on_submit():
		task.content = form.content.data
		task.deadline = form.deadline.data
		db.session.commit()
		return redirect(url_for('tasks.taskmaster'))
	elif request.method == 'GET':
		form.content.data = task.content
		form.deadline.data = task.deadline
	return render_template('/task/update_task.html', task=task, form=form, title='taskmaster')

@tasks.route('/taskmaster/upgrade/<int:id>')
@login_required
def upgrade(id):
	try:
		task = Task.query.filter_by(id=id).first()
		if task.account.email != current_user.email:
			abort(403)
		if task.priority_num == 3:
			task.priority_num = 2
			task.priority = 'Important'
			flash('Your task has been upgraded successfully', 'info')
			db.session.commit()
			return redirect('/taskmaster')
		elif task.priority_num == 2:
			task.priority_num = 1
			task.priority = 'Urgent'
			flash('Your task has been upgraded successfully', 'info')
			db.session.commit()
			return redirect('/taskmaster')
		else:
			return redirect('/taskmaster')
	except Exception as e:
		raise e

@tasks.route('/taskmaster/downgrade/<int:id>')
@login_required
def downgrade(id):
	try:
		task = Task.query.filter_by(id=id).first()
		if task.account.email != current_user.email:
			abort(403)
		if task.priority_num == 1:
			task.priority_num = 2
			task.priority = 'Important'
			flash('Your task has been downgraded successfully', 'info')
			db.session.commit()
			return redirect('/taskmaster')
		elif task.priority_num == 2:
			task.priority_num = 3
			task.priority = 'Just Fine'
			flash('Your task has been downgraded successfully', 'info')
			db.session.commit()
			return redirect('/taskmaster')
		else:
			return redirect('/taskmaster')
	except Exception as e:
		raise e

@tasks.route('/taskmaster/finished/<int:id>')
@login_required
def finished(id):
	try:
		task = Task.query.filter_by(id=id).first()
		if task.account.email != current_user.email:
			abort(403)
		task.completed_num = 1
		task.completed = 'Completed'
		flash('Your task has been finished', 'success')
		db.session.commit()
		return redirect('/taskmaster')
	except:
		raise 

@tasks.route('/taskmaster/all')
@login_required
def all():
	page = request.args.get('page', 1, type=int)
	tasks = Task.query.order_by(Task.completed_num, Task.id.desc()).filter_by(account=current_user)\
							.paginate(page=page, per_page=15)
	return render_template('/task/finished.html', tasks=tasks, title='taskmaster')

@tasks.route('/taskmaster/restore/<int:id>')
@login_required
def restore(id):
	task = Task.query.filter_by(id=id).first()
	if task.account.email != current_user.email:
		abort(403)
	try:
		task.completed_num = 0
		task.completed = 'Not yet'
		flash('Your task has been restored successfully', 'info')
		db.session.commit()
		return redirect('/taskmaster/all')
	except Exception as e:
		raise e
