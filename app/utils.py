import json
import os
from datetime import datetime, timedelta
from random import uniform

from flask import current_app
from flask_mail import Message, Mail

from app import logger

basedir = os.path.abspath(os.path.dirname(__file__))

def send_email(subject: str, recipients: list, body: str = '', html: str = None,
               cc: list = None, bcc: list = None, attachments: list = None, sender: str = None) -> None:
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            body=body,
            html=html if html else f"<h3>{subject}</h3><p>{body}</p>",
            sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER')
        )

        if attachments:
            for filename, content_type, data in attachments:
                msg.attach(filename, content_type, data)

        mail = Mail(current_app)
        mail.send(msg)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def load_buildings_data():
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


def discount_applicator(product_instance):
    category_range = {
    "f": [50, 20],  # f: fruits and Vegetables
    "b": [80, 50],  # b: bakery
    "d": [70, 40],  # d: dairy and related products
    "m": [60, 30],  # m: meat
    "s": [85, 60],  # s: sweets
    "r": [75, 45],  # r: ready to eat
    }
    product_category = product_instance.category
    discount_range = category_range[product_category[0]]
    #logger.debug("discount rate is " + str(product_instance.discount))
    #logger.debug(type(product_instance.discount))
    # To ensure that if no discount rate is given a category based discount, contingent on the category can be used
    discount_rate = (1 - product_instance.discount / 100) if (product_instance.discount is not
                                                              None)  else (uniform(discount_range[0], discount_range[1])) / 100
    date_today = datetime.today()

    if product_instance.expiry_date <= (date_today + timedelta(days=1)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 3)
    elif product_instance.expiry_date <= (date_today + timedelta(days=2)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 2)
    elif product_instance.expiry_date <= (date_today + timedelta(days=3)).date():
        product_instance.final_price = product_instance.marked_price * (discount_rate ** 1)
    return product_instance