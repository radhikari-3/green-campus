from datetime import datetime, timedelta
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import select
from wtforms.validators import ValidationError

from app import app
from app import db
from app.forms import LoginForm, InventoryForm, DeleteForm, EditProductForm
from app.models import User, Inventory

# def discount_applicator(product_instance):
#     # Check expiry date to apply discount
#     if product_instance.expiry_date <= (datetime.today() + timedelta(days=1)).date():
#         product_instance.price *= 0.3  # Apply 70% discount
#     elif product_instance.expiry_date <= (datetime.today() + timedelta(days=2)).date():
#         product_instance.price *= 0.5  # Apply 50% discount
#     elif product_instance.expiry_date <= (datetime.today() + timedelta(days=3)).date():
#         product_instance.price *= 0.7  # Apply 30% discount
#     return product_instance
@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('generic_form.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/smart_food_expiry', methods= ['GET', 'POST'])
@login_required
def smart_food_expiry():
    inventory_form = InventoryForm()
    if inventory_form.validate_on_submit():
        product_name = inventory_form.name.data
        product_expiry_date = inventory_form.expiry_date.data
        product_units = inventory_form.units.data
        product_price = inventory_form.price.data
        # logic for discount and final price
        product_discount = db.session.scalar(select(Inventory.discount).filter_by(name=product_name))
        if product_discount is None or product_discount == 0:
            final_price = product_price
        else:
            final_price = round(product_price * (1 - product_discount), 2)
        product_location = inventory_form.location.data
        existing_product = db.session.scalars(select(Inventory).filter_by(name=product_name)).first()
        # Add new product
        if existing_product is None:
            new_product = Inventory(
                name=product_name,
                expiry_date=product_expiry_date,
                units=product_units,
                marked_price=product_price,
                discount=product_discount,
                final_price=final_price,
                location=product_location,
                user_id=current_user.id
            )
            # new_product = discount_applicator(new_product)
            db.session.add(new_product)
            db.session.commit()
        else:
            existing_product.units += product_units  #a = a + b can be written as a += b
            # existing_product = discount_applicator(existing_product)
            db.session.commit()
        # Notify when a product is sold out
        flash("Product added successfully!", "success")
        session['show_confetti'] = True
        return redirect(url_for('inventory'))
    return render_template('smart_food_expiry.html', title='Smart Food Expiry System', inventory_form=inventory_form, confetti=False)


@app.route('/inventory', methods= ['GET', 'POST'])
@login_required
def inventory():
    delete_product_form = DeleteForm()
    inventory_form = InventoryForm()
    edit_product_form = EditProductForm()
    show_confetti = session.pop('show_confetti', False)
    user_products_list = list(db.session.scalars(select(Inventory).filter_by(user_id=current_user.id)))
    return render_template('inventory.html', title='Current Inventory', user_products_list = user_products_list, confetti=show_confetti , delete_product_form = delete_product_form, edit_product_form=edit_product_form, inventory_form = inventory_form , show_form=False)

@app.route('/delete_product', methods=['GET', 'POST'])
@login_required
def delete_product():
    delete_product_form = DeleteForm()
    product = db.session.scalar(sa.select(Inventory).filter_by(user_id=current_user.id))
    if delete_product_form.validate_on_submit():
        if product is not None:
            db.session.delete(product)
            db.session.commit()
            flash(f'{product.name} successfully deleted', 'success')
            return redirect(url_for('inventory'))
    return redirect(url_for('inventory'))


@app.route('/edit_mode', methods=['GET','POST'])
@login_required
def edit_mode():
    edit_product_form = EditProductForm()
    inventory_form = InventoryForm()
    delete_product_form = DeleteForm()
    show_confetti = session.pop('show_confetti', False)
    user_products_list = list(db.session.scalars(select(Inventory).filter_by(user_id=current_user.id))) #you need this because of the jinja loop
    if edit_product_form.validate_on_submit():
        product_id = edit_product_form.edit_product.data
        product_to_be_edited = db.session.get(Inventory, product_id)
        if product_to_be_edited is None:
            flash ('Product is none', 'danger')
            return redirect(url_for('inventory'))
        # This repopulate the form
        elif inventory_form.edit.data != 1:
            product_id = inventory_form.edit.data
            product_to_be_edited = db.session.get(Inventory, product_id)
            inventory_form = InventoryForm(edit=product_id, name=product_to_be_edited.name,
                                           expiry_date=product_to_be_edited.expiry_date,
                                           units=product_to_be_edited.units, price=product_to_be_edited.marked_price,
                                           location=product_to_be_edited.location)
            product_to_be_edited.name = inventory_form.name.data
            product_to_be_edited.expiry_date = inventory_form.expiry_date.data
            product_to_be_edited.units = inventory_form.units.data
            product_to_be_edited.marked_price = inventory_form.price.data

            db.session.commit()
            flash("Product edited successfully!", "success")
            session['show_confetti'] = True
            return redirect(url_for('inventory'))
        return render_template('inventory.html', title='Edit Product', inventory_form=inventory_form,
                               edit_product_form=edit_product_form, user_products_list=user_products_list,
                               delete_product_form=delete_product_form, show_form=True, confetti=show_confetti, product_to_be_edited=product_to_be_edited)
    return render_template ('inventory.html', title='Edit Product', inventory_form=inventory_form, edit_product_form=edit_product_form, user_products_list= user_products_list, delete_product_form= delete_product_form, show_form=True, confetti=show_confetti)


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