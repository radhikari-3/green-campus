from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import select

from app import app
from app import db
from app.forms import LoginForm, DeleteForm, EditProductForm, AddProductForm
from app.models import User, Inventory

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

@app.route('/smart_food_expiry', methods=['GET','POST'])
@login_required
def smart_food_expiry():
    add_product_form = AddProductForm()
    return render_template('smart_food_expiry.html', title='Smart Food Expiry System', add_product_form=add_product_form, confetti=False)


@app.route('/inventory', methods= ['GET', 'POST'])
@login_required
def inventory():
    delete_product_form = DeleteForm()
    add_product_form = AddProductForm()
    edit_product_form = EditProductForm()
    view = request.args.get("view")
    show_form = request.args.get("show_form", "false") == "true"
    show_confetti = session.pop('show_confetti', False)
    user_products_list = list(db.session.scalars(select(Inventory).filter_by(user_id=current_user.id)))
    return render_template('inventory.html', title='Current Inventory', user_products_list = user_products_list, confetti=show_confetti , delete_product_form = delete_product_form, edit_product_form=edit_product_form, add_product_form = add_product_form ,view=view, show_form=show_form)


@app.route('/add_product', methods=['GET','POST'])
@login_required
def add_product():
    add_product_form = AddProductForm()
    if add_product_form.validate_on_submit():
        product_name = add_product_form.name.data
        product_expiry_date = add_product_form.expiry_date.data
        product_units = add_product_form.units.data
        product_price = add_product_form.price.data

        product_discount = db.session.scalar(select(Inventory.discount).filter_by(name=product_name))
        final_price = product_price if not product_discount else round(product_price * (1 - product_discount), 2)
        product_location = add_product_form.location.data
        existing_product = db.session.scalars(select(Inventory).filter_by(name=product_name)).first()
        if existing_product is None:
            db.session.add(Inventory(name=product_name,expiry_date=product_expiry_date,units=product_units,marked_price=product_price,discount=product_discount,final_price=final_price,location=product_location,user_id=current_user.id))
        else:
            existing_product.units += product_units
        db.session.commit()
        flash("Product added successfully!", "success")
        session['show_confetti'] = True
        return redirect(url_for('inventory'))
    flash("Failed to add product. Please check the form.", "danger")
    return redirect(url_for('smart_food_expiry'))


@app.route('/delete_product', methods=['POST'])
@login_required
def delete_product():
    delete_product_form = DeleteForm()
    product_id = delete_product_form.delete_product.data
    product = db.session.get(Inventory, product_id)
    if delete_product_form.validate_on_submit():
        if product is not None:
            db.session.delete(product)
            db.session.commit()
            flash(f'{product.name} successfully deleted', 'success')
            return redirect(url_for('inventory'))
    return redirect(url_for('inventory'))

@app.route('/edit_product', methods=['GET', 'POST'])
@login_required
def edit_product():
    edit_product_form = EditProductForm()
    add_product_form = AddProductForm()  # For displaying existing structure
    delete_product_form = DeleteForm()
    show_confetti = session.pop('show_confetti', False)
    user_products_list = list(db.session.scalars(select(Inventory).filter_by(user_id=current_user.id)))
    view = request.args.get("view")

    # Handle GET request to populate the form
    if request.method == 'GET':
        product_id = request.args.get('product_id')
        if product_id:
            product = db.session.get(Inventory, product_id)
            if product:
                # Populate the form with product data
                edit_product_form.product_id.data = product.id
                edit_product_form.name.data = product.name
                edit_product_form.expiry_date.data = product.expiry_date
                edit_product_form.units.data = product.units
                edit_product_form.price.data = product.marked_price
                edit_product_form.location.data = product.location
            else:
                flash('Product not found.', 'danger')
                return redirect(url_for('inventory', view=view))

    # Handle POST request to update the product
    if request.method == 'POST' and edit_product_form.validate_on_submit():
        product_id = edit_product_form.product_id.data
        product = db.session.get(Inventory, product_id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('inventory', view=view))
        else:
            # Update product fields
            print("product updating")
            update_product_fields(product, edit_product_form)
            db.session.commit()

            flash("Product updated successfully!", "success")
            session['show_confetti'] = True
            return redirect(url_for('inventory', view=view))

    return render_template('inventory.html',title='Edit Product',add_product_form=add_product_form,edit_product_form=edit_product_form,user_products_list=user_products_list,delete_product_form=delete_product_form,show_form=True,confetti=show_confetti, view=view)


def update_product_fields(product, edit_product_form):
    """Helper function to update product fields from the form."""
    product.name = edit_product_form.name.data
    product.expiry_date = edit_product_form.expiry_date.data
    product.units = edit_product_form.units.data
    product.marked_price = edit_product_form.price.data
    product.location = edit_product_form.location.data
    product.final_price = edit_product_form.price.data


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