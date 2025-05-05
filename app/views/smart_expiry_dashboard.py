# views.py
from datetime import datetime
from datetime import timedelta
from random import uniform

from dateutil.utils import today
from flask import render_template, Blueprint
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.sql.functions import func

from app import db
from app.models import Inventory, ActivityLog

smart_exp_bp = Blueprint('smart_exp', __name__)

@smart_exp_bp.route('/view_expiring_products', methods= ['GET'])
@login_required
def view_expiring_products():
    return render_template('expiring_products.html', title="Products expiring soon")

@smart_exp_bp.route("/expiring-offers/<category>", methods = ["GET", "POST"])
@login_required
def expiring_offers(category):
    total_points, pounds = calculate_user_eco_points(current_user.email)
    category_map = {
        "f": "Fruits & Vegetable related products",  # f: fruits and Vegetables
        "g": "Grains & related products",  # g: grains
        "d": "Dairy & dairy related products",  # d: dairy and related products
        "n": "Nuts & related products",  # n: nuts
    }
    relevant_products = Inventory.query.filter(Inventory.category == category).all()
    relevant_title = "Best offers on " + category_map[category]
    return render_template("category_wise_products.html",title= relevant_title, relevant_products = relevant_products, total_points = total_points, pounds = pounds)


def calculate_user_eco_points(email):
    total_points = db.session.query(func.sum(ActivityLog.eco_points)).filter(ActivityLog.email == email).scalar() or 0
    pounds = round(total_points * 0.02, 2)
    return [total_points, pounds]


def discount_applicator(product_instance):
    category_range = {
        "f": [70, 30],  # f: fruits and Vegetables
        "g": [90, 60],  # g: grains
        "d": [80, 40],  # d: dairy and related products
        "n": [90, 70],  # n: nuts
    }
    product_category = product_instance.category
    discount_range = category_range[product_category[0]]
    #logger.debug("discount rate is " + str(product_instance.discount))
    #logger.debug(type(product_instance.discount))
    # To ensure that if no discount rate is given a category based discount, contingent on the category can be used
    discount_rate = (1 - product_instance.discount / 100) if product_instance.discount is not None  else (uniform(discount_range[0], discount_range[1])) / 100
    date_today = datetime.today()

    if product_instance.expiry_date <= (date_today + timedelta(days=1)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 3)
    elif product_instance.expiry_date <= (date_today + timedelta(days=2)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 2)
    elif product_instance.expiry_date <= (date_today + timedelta(days=3)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 1)
    return product_instance

def get_updated_daily_discounts(time_limit):
    time_limit = datetime.today() + timedelta(days=time_limit)
    inventory_list = db.session.scalars(select(Inventory).where(Inventory.expiry_date >= today(), Inventory.expiry_date <= time_limit)).all()
    for index in range(len(inventory_list)):
        inventory_list[index] = discount_applicator(inventory_list[index])
    db.session.commit()
    return inventory_list

