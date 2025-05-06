from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import select

from app import db
from app.forms import AddProductForm, DeleteForm, EditProductForm
from app.models import Inventory

vendors_bp = Blueprint('vendors', __name__)

def get_user_products(user_id):
    """Fetch all products for the current user."""
    return list(db.session.scalars(select(Inventory).filter_by(user_id=user_id)))

def populate_edit_form(product, form):
    """Populate the edit form with product data."""
    form.product_id.data = product.id
    form.name.data = product.name
    form.expiry_date.data = product.expiry_date
    form.units.data = product.units
    form.price.data = product.marked_price
    form.location.data = product.location

def update_product_fields(product, form):
    """Update product fields from the form."""
    product.name = form.name.data
    product.expiry_date = form.expiry_date.data
    product.units = form.units.data  # Ensure units are updated
    product.marked_price = form.price.data
    product.location = form.location.data
    product.final_price = form.price.data  # Update final price if necessary

@vendors_bp.route('/smart_food_expiry', methods=['GET', 'POST'])
@login_required
def smart_food_expiry():
    add_product_form = AddProductForm()
    return render_template('smart_food_expiry.html',
                           title='Smart Food Expiry System',
                           add_product_form=add_product_form,
                           confetti=False)

@vendors_bp.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    delete_product_form = DeleteForm()
    add_product_form = AddProductForm()
    edit_product_form = EditProductForm()
    view = request.args.get("view")
    show_form = request.args.get("show_form", "false") == "true"
    show_confetti = session.pop('show_confetti', False)
    user_products_list = get_user_products(current_user.id)
    return render_template('inventory.html', title='Current Inventory',
                           user_products_list=user_products_list, confetti=show_confetti,
                           delete_product_form=delete_product_form, edit_product_form=edit_product_form,
                           add_product_form=add_product_form, view=view, show_form=show_form)

@vendors_bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    add_product_form = AddProductForm()
    if add_product_form.validate_on_submit():
        product_name = add_product_form.name.data
        product_expiry_date = add_product_form.expiry_date.data
        product_units = add_product_form.units.data
        product_category = add_product_form.category.data
        product_price = add_product_form.price.data
        product_location = add_product_form.location.data

        product_discount = db.session.scalar(select(Inventory.discount).filter_by(name=product_name))
        final_price = product_price if product_discount is None else round(product_price * (1 - product_discount), 2)
        existing_product = db.session.scalars(select(Inventory).filter_by(name=product_name)).first()

        if existing_product is None:
            db.session.add(Inventory(name=product_name,
                                     expiry_date=product_expiry_date,
                                     units=product_units,
                                     category=product_category,
                                     marked_price=product_price,
                                     discount=product_discount,
                                     final_price=final_price,
                                     location=product_location,
                                     user_id=current_user.id))
        else:
            existing_product.units += product_units

        db.session.commit()
        flash("Product added successfully!", "success")
        session['show_confetti'] = True
        return redirect(url_for('vendors.inventory'))

    flash("Failed to add product. Please check the form.", "danger")
    return redirect(url_for('vendors.smart_food_expiry'))

@vendors_bp.route('/delete_product', methods=['POST'])
@login_required
def delete_product():
    delete_product_form = DeleteForm()
    if delete_product_form.validate_on_submit():
        product_id = delete_product_form.delete_product.data
        product = db.session.get(Inventory, product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            flash(f'{product.name} successfully deleted', 'success')
        else:
            flash('Product not found.', 'danger')
    return redirect(url_for('vendors.inventory'))

@vendors_bp.route('/edit_product', methods=['GET', 'POST'])
@login_required
def edit_product():
    edit_product_form = EditProductForm()
    view = request.args.get("view")

    if request.method == 'GET':
        product_id = request.args.get('product_id')
        if product_id:
            product = db.session.get(Inventory, product_id)
            if product:
                populate_edit_form(product, edit_product_form)
            else:
                flash('Product not found.', 'danger')
                return redirect(url_for('vendors.inventory', view=view))

    if request.method == 'POST' and edit_product_form.validate_on_submit():
        product_id = edit_product_form.product_id.data
        product = db.session.get(Inventory, product_id)
        if product:
            update_product_fields(product, edit_product_form)  # Update all fields, including units
            db.session.commit()  # Commit changes to the database
            flash("Product updated successfully!", "success")
            session['show_confetti'] = True
        else:
            flash('Product not found.', 'danger')
        return redirect(url_for('vendors.inventory', view=view))

    user_products_list = get_user_products(current_user.id)
    return render_template('inventory.html',
                           title='Edit Product',
                           add_product_form=AddProductForm(),
                           edit_product_form=edit_product_form,
                           user_products_list=user_products_list,
                           delete_product_form=DeleteForm(),
                           show_form=True,
                           confetti=session.pop('show_confetti', False),
                           view=view)
