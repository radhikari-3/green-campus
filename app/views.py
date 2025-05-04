import logging
import os
from datetime import datetime, timedelta, time
from smtplib import SMTPRecipientsRefused, SMTPException
#views.py
from urllib.parse import urlsplit
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.oauth_config import send_email_via_gmail
from datetime import datetime
import sqlalchemy as sa
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dateutil.utils import today
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask.cli import load_dotenv
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Mail, Message
from sqlalchemy import select
from sqlalchemy.sql.functions import random
from unicodedata import category

from app import app, mail
from app import db
from app.forms import LoginForm, InventoryForm
from app.models import User, Inventory

# Load the environment variables from .env
load_dotenv()

# Load the scheduler
scheduler = BackgroundScheduler()


def discount_applicator(product_instance):
    category_range = {
        "f": [70, 30],  # f: fruits and Vegetables
        "g": [90, 60],  # g: grains
        "d": [80, 40],  # d: dairy and related products
        "n": [90, 70],  # n: nuts
    }
    product_category = product_instance.category
    discount_range = category_range[product_category[0]]

    # To ensure that if no discount rate is given a category based discount, contingent on the category can be used
    discount_rate = (1 - product_instance.discount / 100) if product_instance.discount not in [0, None] else (random.uniform(discount_range[0], discount_range[1])) / 100

    # Above line is same as below

    # if product_instance.discount not in [0, None]:
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

from app import app, db
from app.forms import LoginForm, VerifyEmailForm, SignupForm, ResetPasswordForm, ResetPasswordRequestForm, PasswordChangeForm, ResetOTPForm
from app.models import User
import sys

@app.route("/")
def home():
    return render_template('home.html', title="Home")

@app.route('/account')
@login_required
def account():
    days_since = (datetime.utcnow() - current_user.signup_date).days
    return render_template('account.html', title="Account", days_since_signup = days_since)


# helper to get serializer
def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

# --- SIGNUP ---
@app.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        existing = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if existing:
            flash('Email already registered','danger')
            return redirect(url_for('signup'))
        u = User(email=form.email.data)
        u.set_password(form.password.data)
        otp = u.generate_otp()
        db.session.add(u); db.session.commit()

        send_email_via_gmail(
            to = u.email,
            subject = "Your Verification Code",
            body = f"Your signup code is {otp}. It expires in 10 minutes."
        )
        flash('OTP sent to your email.','info')
        return redirect(url_for('verify_email', user_id=u.id))
    return render_template('generic_form.html', title='Sign Up', form=form)


@app.route('/verify/<int:user_id>', methods=['GET','POST'])
def verify_email(user_id):
    u = db.session.get(User, user_id)
    form = VerifyEmailForm()
    if form.validate_on_submit():
        if u.email_otp == form.otp.data and u.email_otp_expires > datetime.utcnow():
            u.email_verified = True
            u.email_otp = None
            u.email_otp_expires = None
            db.session.commit()
            flash('Email verified! You can now log in.','success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired OTP.','danger')
    return render_template('generic_form.html', title='Verify Email', form=form)


@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = ResetPasswordRequestForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        u = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if u and u.email_verified:
            otp = u.generate_otp()
            db.session.commit()
            send_email_via_gmail(
                to=u.email,
                subject="Password reset OTP",
                body=f"Your OTP is {otp} (valid 10 min)."
            )
            flash('OTP sent to your email.', 'info')
        return redirect(url_for('forgot_password_verify', user_id=u.id))
    return render_template('generic_form.html', title='Forgot Password', form=form)

@app.route('/forgot_password_verify/<int:user_id>', methods=['GET','POST'])
def forgot_password_verify(user_id):
    form = ResetOTPForm()
    u = db.session.get(User, user_id)
    if form.validate_on_submit():
        if (u.email_otp == form.otp.data
            and u.email_otp_expires > datetime.utcnow()):
            u.email_otp = None
            u.email_otp_expires = None
            db.session.commit()
            return redirect(url_for('forgot_password_reset', user_id=user_id))
        flash('Invalid or expired OTP.', 'danger')
    return render_template('generic_form.html', title='Verify OTP', form=form)

@app.route('/forgot_password_reset/<int:user_id>', methods=['GET','POST'])
def forgot_password_reset(user_id):
    form = ResetPasswordForm()
    u = db.session.get(User, user_id)
    if form.validate_on_submit():
        u.set_password(form.password.data)
        u.signup_date = datetime.utcnow()
        db.session.commit()
        flash('Your password has been reset. You may now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('generic_form.html', title='New Password', form=form)


@app.route('/reset_password', methods=['GET','POST'])
@login_required
def reset_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password incorrect.', 'danger')
            return redirect(url_for('reset_password'))
        current_user.set_password(form.new_password.data)
        current_user.signup_date = datetime.utcnow()
        db.session.commit()
        flash('Your password has been changed.', 'success')
        return redirect(url_for('account'))
    return render_template('generic_form.html', title='Change Password', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        if not user.email_verified:
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/smart_food_expiry', methods= ['GET', 'POST'])
@login_required
def smart_food_expiry():
    inventory_form = InventoryForm()
    if inventory_form.validate_on_submit():
        product_name = inventory_form.name.data
        product_expiry_date = inventory_form.expiry_date.data
        product_units = inventory_form.units.data
        product_marked_price = inventory_form.marked_price.data
        product_discount = inventory_form.discount.data
        product_location = inventory_form.location.data
        product_category = inventory_form.category.data
        existing_product = db.session.scalars(select(Inventory).filter_by(name=product_name)).first()
        # Add new product
        if existing_product is None:
            new_product = Inventory(name=product_name, expiry_date=product_expiry_date, units=product_units,
                                    marked_price=product_marked_price,final_price = product_marked_price, user_id=current_user.id, discount = product_discount, location = product_location, category =product_category )
            print("category:   " + product_category)
            new_product = discount_applicator(new_product)
            db.session.add(new_product)
            db.session.commit()
        else:
            existing_product.units += product_units  #a = a + b can be written as a += b
            existing_product = discount_applicator(existing_product)
            db.session.commit()
            # Notify when a product is sold out

        return redirect(url_for('inventory'))
    return render_template('smart_food_expiry.html', title='Smart Food Expiry System', inventory_form=inventory_form)


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
    category_map = {
        "f": "Fruits & Vegetable related products",  # f: fruits and Vegetables
        "g": "Grains & related products",  # g: grains
        "d": "Dairy & dairy related products",  # d: dairy and related products
        "n": "Nuts & related products",  # n: nuts
    }
    relevant_products = Inventory.query.filter(Inventory.category == category).all()
    relevant_title = "Best offers on " + category_map[category]
    return render_template("category_wise_products.html",title= relevant_title, relevant_products = relevant_products)





@app.route('/inventory', methods= ['GET', 'POST'])
@login_required
def inventory():
    inventory_list = db.session.scalars(select(Inventory).filter_by(user_id=current_user.id))
    return render_template('inventory.html', title='Current Inventory', inventory_list=inventory_list)


@app.route('/view_expiring_products', methods= ['GET'])
@login_required
def view_expiring_products():
    return render_template('expiring_products.html', title="Products expiring soon")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


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


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500


def start_scheduler(self):
        # This will start the scheduler once the first request is received
        if not scheduler.running:
            scheduler.start()
            print("Scheduler started in controller!")