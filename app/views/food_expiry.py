# === Imports ===
from datetime import datetime, timedelta

from dateutil.utils import today
from flask import render_template, Blueprint
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.sql.functions import func

from app import db
from app.models import Inventory, ActivityLog
from app.utils import discount_applicator

# === Blueprint Setup ===
smart_exp_bp = Blueprint('smart_exp', __name__)


# === Route: Expiring Products Landing Page ===
@smart_exp_bp.route('/view_expiring_products', methods=['GET'])
@login_required
def view_expiring_products():
    """
    Renders a general view for all expiring products.
    """
    return render_template('expiring_products.html', title="Products expiring soon")


# === Route: Category-Wise Expiring Offers ===
@smart_exp_bp.route("/expiring-offers/<category>", methods=["GET", "POST"])
@login_required
def expiring_offers(category):
    """
    Displays discount offers for products by category.
    Also calculates user's eco points and equivalent pounds.
    """
    total_points, pounds = calculate_user_eco_points(current_user.email)

    category_map = {
        "f": "Fruits and Vegetables",
        "b": "Bakery",
        "d": "Dairy & dairy related products",
        "m": "Nuts & related products",
        "s": "Sweets",
        "r": "Ready to Eat"
    }

    # Fetch all products from the selected category
    relevant_products = Inventory.query.filter(Inventory.category == category).all()
    relevant_title = "Best offers on " + category_map[category]

    # Get unique store locations from the database
    locations = db.session.execute(select(Inventory.location).distinct()).scalars().all()

    return render_template("category_wise_products.html",
                           title=relevant_title,
                           relevant_products=relevant_products,
                           total_points=total_points,
                           locations=locations,
                           pounds=pounds)


# === Helper: Calculate Total Eco Points and Convert to £ ===
def calculate_user_eco_points(email):
    """
    Returns total eco points and their equivalent value in pounds (1 point = £0.02).
    """
    total_points = db.session.query(func.sum(ActivityLog.eco_points))\
                    .filter(ActivityLog.email == email).scalar() or 0
    pounds = round(total_points * 0.02, 2)
    return [total_points, pounds]


# === Helper: Get Inventory Items with Updated Discounts ===
def get_updated_daily_discounts(time_limit):
    """
    Fetches inventory items expiring within the given time limit (in days),
    applies tiered discount logic, and commits updated prices to DB.
    """
    time_limit = datetime.today() + timedelta(days=time_limit)

    inventory_list = db.session.scalars(
        select(Inventory).where(
            Inventory.expiry_date >= today(),
            Inventory.expiry_date <= time_limit
        )
    ).all()

    for index in range(len(inventory_list)):
        inventory_list[index] = discount_applicator(inventory_list[index])

    db.session.commit()
    return inventory_list
