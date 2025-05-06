#main.py
from flask import render_template, Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template('home.html', title="Home")

@main_bp.route("/new_dashboard")
def _new_home():
    return render_template('dashboard_base.html', title="Home")


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@main_bp.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@main_bp.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@main_bp.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@main_bp.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500