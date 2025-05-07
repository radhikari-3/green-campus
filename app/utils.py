import json
import os
from datetime import datetime, timedelta
from random import uniform

from flask import current_app
from flask_mail import Message, Mail

from app import logger

# Base directory for accessing local files
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
    Sends an email using Flask-Mail with optional HTML, CC, BCC, and attachments.
    - Fallback HTML is created if none is provided.
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

    # Add attachments if any
    if attachments:
        for filename, content_type, data in attachments:
            msg.attach(filename, content_type, data)

    # Send email using Flask-Mail instance
    mail = Mail(current_app)
    mail.send(msg)


# === Load Building Data for IoT/Analytics ===
def load_buildings_data():
    """
    Loads building metadata from a JSON file for use in sensor simulations or analytics.
    Returns:
        university_buildings (list), accommodation_buildings (list)
    """
    file_path = os.path.join(basedir, 'static', 'buildings_data.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            university_buildings = data.get('university_buildings', [])
            accommodation_buildings = data.get('accommodation_buildings', [])
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        university_buildings = []
        accommodation_buildings = []

    return university_buildings, accommodation_buildings


# === Discount Calculator Based on Expiry and Category ===
def discount_applicator(product_instance):
    """
    Dynamically applies tiered discounts to a product based on:
    - Its expiry date (closer = higher discount)
    - Its category (each has its own discount range)

    If a manual discount exists, it's used. Otherwise, a random one is generated based on category logic.
    Returns:
        product_instance with updated `final_price`
    """

    # Category-wise discount ranges [max%, min%]
    category_range = {
        "f": [50, 20],  # Fruits & Vegetables
        "b": [80, 50],  # Bakery
        "d": [70, 40],  # Dairy
        "m": [60, 30],  # Meat
        "s": [85, 60],  # Sweets
        "r": [75, 45],  # Ready to Eat
    }

    product_category = product_instance.category
    discount_range = category_range[product_category[0]]  # Use first character as key

    # If discount exists, convert to fraction. If not, generate one from range.
    discount_rate = (
        (1 - product_instance.discount / 100)
        if (product_instance.discount is not None)
        else (uniform(discount_range[0], discount_range[1]) / 100)
    )

    date_today = datetime.today()

    # Apply discount based on proximity to expiry (closer = more aggressive reduction)
    if product_instance.expiry_date <= (date_today + timedelta(days=1)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 3)
    elif product_instance.expiry_date <= (date_today + timedelta(days=2)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 2)
    elif product_instance.expiry_date <= (date_today + timedelta(days=3)).date():
        product_instance.final_price = product_instance.marked_price * discount_rate

    return product_instance
