# === Imports ===
from flask import render_template, Blueprint

# === Blueprint Setup ===
main_bp = Blueprint('main', __name__)


# === Route: Home Page ===
@main_bp.route("/")
def home():
    """
    Renders the public-facing homepage.
    """
    return render_template('home.html', title="Home")


# === Route: New Dashboard Base Template (Test/Preview) ===
@main_bp.route("/new_dashboard")
def _new_home():
    """
    Renders a new dashboard base layout (likely for internal preview or development).
    """
    return render_template('dashboard_base.html', title="Home")


# === Error Handlers ===
# Reference: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# --- 403 Forbidden ---
@main_bp.errorhandler(403)
def error_403(error):
    """
    Custom page for HTTP 403 - Forbidden.
    """
    return render_template('errors/403.html', title='Error'), 403

# --- 404 Not Found ---
@main_bp.errorhandler(404)
def error_404(error):
    """
    Custom page for HTTP 404 - Page Not Found.
    """
    return render_template('errors/404.html', title='Error'), 404

# --- 413 Payload Too Large ---
@main_bp.errorhandler(413)
def error_413(error):
    """
    Custom page for HTTP 413 - Payload Too Large.
    """
    return render_template('errors/413.html', title='Error'), 413

# --- 500 Internal Server Error ---
@main_bp.errorhandler(500)
def error_500(error):
    """
    Custom page for HTTP 500 - Internal Server Error.
    """
    return render_template('errors/500.html', title='Error'), 500
