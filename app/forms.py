import datetime

from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, HiddenField, PasswordField, SubmitField, BooleanField, DateField, \
    IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Email, EqualTo


def validate_expiry_date(self, field):
    today = datetime.date.today()  # Get today's date (no time part)
    if field.data < today:  # field.data is already a date (because you're using DateField)
        raise ValidationError("Expiry date cannot be in the past. Please select a valid future date.")

class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Email is required."), Email(message="Enter a valid email address.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(message="Product name is required.")])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[
        DataRequired(message="Expiry date is required."),
        validate_expiry_date
    ])
    units = IntegerField('Units', validators=[
        NumberRange(1, 30, message="Units must be between 1 and 30.")
    ])
    price = FloatField('Price (£)', validators=[
        DataRequired(message="Price is required.")
    ])
    category = SelectField('Product Category', validators=[DataRequired(message="Please select a product category.")],
                           choices=[("f", "Fruits and Vegetables"), ("g", "Grains and Breads"),
                                    ("d", "Dairy and Animal products"), ("n", "Nuts")])
    discount = FloatField('Discount Rate (%)', validators=[
        InputRequired(message="Discount rate is required."),
        NumberRange(0, 100, message="Discount rate must be between 0% and 100%.")
    ])
    location = StringField('Location', validators=[DataRequired(message="Location is required.")])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    delete_product = HiddenField('delete_product')

class EditProductForm(FlaskForm):
    product_id = HiddenField('Product ID', default="-1")
    name = StringField('Product Name', validators=[DataRequired(message="Product name is required.")])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[
        DataRequired(message="Expiry date is required."),
        validate_expiry_date
    ])
    units = IntegerField('Units', validators=[
        NumberRange(1, 30, message="Units must be between 1 and 30.")
    ])
    price = FloatField('Price (£)', validators=[
        DataRequired(message="Price is required.")
    ])
    category = SelectField('Product Category', validators=[DataRequired(message="Please select a product category.")],
                           choices=[("f", "Fruits and Vegetables"), ("g", "Grains and Breads"),
                                    ("d", "Dairy and Animal products"), ("n", "Nuts")])

    location = StringField('Location', validators=[DataRequired(message="Location is required.")])
    submit = SubmitField('Update')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Password confirmation is required."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Sign Up')

class VerifyEmailForm(FlaskForm):
    otp = StringField('OTP Code', validators=[DataRequired(message="OTP code is required.")])
    submit = SubmitField('Verify Email')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address.")
    ])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(message="New password is required.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Password confirmation is required."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Reset Password')

class ResetOTPForm(FlaskForm):
    otp = StringField('OTP Code', validators=[DataRequired(message="OTP code is required.")])
    submit = SubmitField('Verify OTP')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(message="Current password is required.")])
    new_password = PasswordField('New Password', validators=[DataRequired(message="New password is required.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Password confirmation is required."),
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField('Change Password')
