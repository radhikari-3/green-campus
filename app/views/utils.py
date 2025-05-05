
from flask import Blueprint, request, flash, redirect, url_for
from flask_mail import Message

from app import mail

utils_bp = Blueprint('utils', __name__)


@utils_bp.route('/send_email', methods=['GET','POST'])
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
