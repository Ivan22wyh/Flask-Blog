from flask import Blueprint, render_template, url_for

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def error_404(error):
    return render_template('/error/404.html', title='404 error'), 404

@errors.app_errorhandler(403)
def error_403(error):
    return render_template('/error/403.html', title='403 error'), 403

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('/error/500.html', title='500 error'), 500

