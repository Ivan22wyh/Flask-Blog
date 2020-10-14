from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user
from flask import redirect, url_for, abort

    
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login', next='admin'))
        elif current_user.username != 'root':
            abort(403)
        return super(MyAdminIndexView, self).index()

class CustomModelView(ModelView):

    def is_accessible(self):
        return current_user.username=='root'

class MyUserView(CustomModelView):
    can_delete = False
    can_edit = False
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_searchable_list = ['username', 'email']
    page_size = 20

class MyTaskView(CustomModelView):
    can_delete = False
    can_edit = False
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_searchable_list = ['content', 'deadline']
    page_size = 5

class MyPostView(CustomModelView):
    can_delete = True
    can_edit = False
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_searchable_list = ['title', 'content']
    page_size = 50

class MyMessageView(CustomModelView):
    can_delete = False
    can_edit = False
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_searchable_list = ['sender_id', 'recipient_id', 'content']
    page_size = 200

class CustomFileAdmin(FileAdmin):
    
    def is_accessible(self):
        return current_user.username=='root'