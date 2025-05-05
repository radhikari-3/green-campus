import logging
import os
from datetime import datetime, timedelta, time
from random import uniform
from smtplib import SMTPRecipientsRefused, SMTPException
#views.py
import io
import qrcode
from urllib.parse import urlsplit
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import sqlalchemy as sa
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dateutil.utils import today
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask.cli import load_dotenv
from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Mail, Message
from sqlalchemy import select
from sqlalchemy.sql.functions import random, func
from unicodedata import category

from app import app, mail
from app import db
from app.forms import LoginForm, InventoryForm
from app.models import User, Inventory, ActivityLog

# Load the environment variables from .env
load_dotenv()

# Load the scheduler
scheduler = BackgroundScheduler()

@app.route('/send_email', methods=['GET','POST'])
def send_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        body = request.form["body"]
        subject = request.form["subject"]
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        msg.html = "<h1>" + subject + "</h1>" + "<p>" + body + "</p>"
        mail.send(msg)
        flash(f'A test message was sent to {recipient}.')
        return redirect(url_for('home'))
    return redirect(url_for('home'))


def send_discount_email():
        with app.app_context():
            recipients =  [user_entity.email.strip()
                for user_entity in db.session.scalars(select(User)).all()
                if user_entity.email]
            print("recipients are " + ",".join(recipients))
            # update the database with appropriate discounts
            get_updated_daily_discounts(3)
            # get products expiring in one day
            relevant_products = get_updated_daily_discounts(1)
            if len(relevant_products) > 0:
                subject = "Items with major discounts, expiring in 1 day! 🌱"

                table_html = "<table border='1' cellspacing='0' cellpadding='4'>"
                table_html += """
                           <tr>
                               <th>Products</th>
                               <th>Expiry Date</th>
                               <th>Units</th>
                               <th>Marked Price</th>
                               <th>Final Price</th>
                               <th>Location</th>
                           </tr>
                       """
                for item in relevant_products:
                    table_html += f"""
                               <tr>
                                   <td>{item.name}</td>
                                   <td>{item.expiry_date.strftime('%Y-%m-%d')}</td>
                                   <td>{item.units}</td>
                                   <td>£{item.marked_price:.2f}</td>
                                   <td>£{item.final_price:.2f}</td>
                                   <td>{item.location}</td>
                               </tr>
                           """
                table_html += "</table>"

                msg = Message(subject, bcc=recipients)

                text_body = "Name | Expiry | Units | Marked Price | Final Price | Location \n"
                text_body += "-" * 60 + "\n"
                for item in relevant_products:
                    text_body += f"{item.name} | {item.expiry_date.strftime('%Y-%m-%d')} | {item.units} | £{item.marked_price:.2f} | £{item.final_price:.2f}\n"

                text_body += "\n\n© 2025 Green Campus Initiative. Empowering Sustainable Change."

                msg.body = text_body

                msg.html = f"""
                <div style="background-color: #f4fcf7; padding: 20px;">
                    <h2 style="text-align: center;">{subject}</h2>
                    <p style="text-align: center;">🍇 Here are our products with exciting offers which expire soon:</p>
                    <div style="display: flex; justify-content: center;">
                        {table_html}
                    </div>
                    <br><hr>
                    <p style="font-size: 0.9em; color: gray; text-align: center;">
                        © 2025 Green Campus Initiative. Empowering Sustainable Change.
                    </p>
                </div>
                """

                try:
                    mail.send(msg)
                except SMTPRecipientsRefused as e:
                    print("One or more recipients were refused:", e.recipients)
                    logging.error("One or more recipients were refused:", e.recipients)
                    flash("Some emails could not be delivered.")
                except SMTPException as e:
                    print("SMTP error occurred:", str(e))
                    flash("An error occurred while sending the email.")
            else:
                print("No relevant products available for discount email. No email sent.")
                logging.info("No relevant products available for discount email. No email sent.")
                # Optionally, flash here if you want users to be informed

@app.route("/expiring-offers/<category>", methods = ["GET", "POST"])
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
    print("discount rate is " + str(product_instance.discount))
    print(type(product_instance.discount))
    # To ensure that if no discount rate is given a category based discount, contingent on the category can be used
    discount_rate = (1 - product_instance.discount / 100) if product_instance.discount is not None  else (uniform(discount_range[0], discount_range[1])) / 100

    # Above line is same as below

    # if product_instance.discount not in None:
    #     discount_rate = (1 - product_instance.discount / 100)
    # else:
    #     random.uniform(discount_range[0], discount_range[1]) / 100

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

def get_next_9am():
    now = datetime.now()
    today_9am = datetime.combine(now.date(), time(9, 0))

    if now < today_9am:
        return today_9am  # today at 9 AM
    else:
        return today_9am + timedelta(days=1)

    # Add the task to the scheduler
scheduler.add_job(
    func=send_discount_email,
    # trigger=IntervalTrigger(seconds=50),
    trigger=IntervalTrigger(hours=24, start_date=get_next_9am()),
    id='discount_offers',
    name='Runs once everyday',
    replace_existing=True
)

def start_scheduler(self):
    # This will start the scheduler once the first request is received
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started in controller!")