import json
import os
from datetime import datetime, timedelta
from random import uniform

from flask import current_app
from flask_mail import Message, Mail

from app import logger, db
from app.models import Building

# === Base Path Setup ===
# Used to construct paths for accessing static files
basedir = os.path.abspath(os.path.dirname(__file__))


# === Generic Email Sender Utility ===

def send_email(
        subject: str,
        recipients: list,
        body: str = '',
        html: str = None,
        cc: list = None,
        bcc: list = None,
        attachments: list = None,
        sender: str = None
) -> None:
    """
    Sends an email using Flask-Mail.

    Arguments:
    - subject: Subject of the email.
    - recipients: List of primary recipient email addresses.
    - body: Plain-text body content.
    - html: Optional HTML version (auto-generated from body if not provided).
    - cc, bcc: Optional CC/BCC email address lists.
    - attachments: Optional list of (filename, mimetype, data) tuples.
    - sender: Overrides the default sender if needed.
    """

    msg = Message(
        subject=subject,
        recipients=recipients,
        cc=cc,
        bcc=bcc,
        body=body,
        html=html if html else f"<h3>{subject}</h3><p>{body}</p>",
        sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER')
    )

    # Attach any provided files to the email
    if attachments:
        for filename, content_type, data in attachments:
            msg.attach(filename, content_type, data)

    # Use a new Mail instance with app context to send the message
    mail = Mail(current_app)
    mail.send(msg)


# === Load Building Metadata for Sensors & Analytics ===

def load_and_insert_buildings():
    """
    Loads building metadata from JSON and inserts all buildings (including flats)
    into the Building table. Returns lists of university and accommodation buildings.
    """
    file_path = os.path.join(basedir, 'static', 'buildings_data.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            university = data.get('university_buildings', [])
            accommodation = data.get('accommodation_buildings', [])

            for b in university:
                db.session.add(Building(
                    name=b.get('building'),
                    code=b.get('building_code', ''),
                    zone=b.get('zone', '')
                ))

            for b in accommodation:
                total_flats = b.get("total_flats", 0)
                base_name = b.get("building")
                for flat_num in range(1, total_flats + 1):
                    db.session.add(Building(
                        name=f"{base_name} Flat {flat_num}",
                        code=b.get('building_code', ''),
                        zone=b.get('zone', '')
                    ))

            db.session.commit()
            return university, accommodation

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return [], []


# === Discount Engine for Expiring Products ===

def discount_applicator(product_instance):
    """
    Calculates and applies a discount to a product based on:
    1. Its category (each has a max-min range for discount)
    2. Its expiry date (closer = heavier discount)
    3. A manually specified discount (if present) is prioritized

    Returns:
        The same product_instance with updated final_price field.
    """

    # Define max and min discount % per category
    category_range = {
        "f": [50, 20],  # Fruits & Vegetables
        "b": [80, 50],  # Bakery
        "d": [70, 40],  # Dairy
        "m": [60, 30],  # Meat
        "s": [85, 60],  # Sweets
        "r": [75, 45],  # Ready to Eat
    }

    # Extract range based on product's category (first char used as key)
    product_category = product_instance.category
    discount_range = category_range[product_category[0]]

    # Determine discount rate:
    # - Use specified discount if present
    # - Otherwise, generate random discount from category range
    discount_rate = (
        (1 - product_instance.discount / 100)
        if (product_instance.discount is not None)
        else (uniform(discount_range[0], discount_range[1]) / 100)
    )

    date_today = datetime.today()

    # Apply deeper discount the closer the product is to expiry
    if product_instance.expiry_date <= (date_today + timedelta(days=1)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 3)
    elif product_instance.expiry_date <= (date_today + timedelta(days=2)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 2)
    elif product_instance.expiry_date <= (date_today + timedelta(days=3)).date():
        product_instance.final_price = product_instance.marked_price * discount_rate

    return product_instance
