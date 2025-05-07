import datetime

# Flask-WTF and WTForms imports for building forms and handling validation
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField
from wtforms.fields import DateField, IntegerField, FloatField, SelectField
from wtforms.validators import (
    DataRequired, NumberRange, Optional, Email, EqualTo, ValidationError
)

# === Custom Validator ===
def validate_expiry_date(self, field):
    """
    Validates that the expiry date is not in the past.
    """
    today = datetime.date.today()
    if field.data < today:
        raise ValidationError("You can't upload expired goods!")

# === Basic Form for Choice Handling via Hidden Field ===
class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

# === User Login Form ===
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# === Product Submission Form ===
class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[DataRequired(), validate_expiry_date])
    units = IntegerField('Units', validators=[NumberRange(1, 30, "You can only upload from 1 to 30 units.")])
    price = FloatField('Price', validators=[DataRequired()])
    category = SelectField('Product Category', validators=[DataRequired()],
        choices=[
            ("f", "Fruits and Vegetables"),
            ("b", "Bakery"),
            ("d", "Dairy"),
            ("m", "Meat"),
            ("s", "Sweets"),
            ("r", "Ready to Eat")
        ])
    discount = FloatField('Discount Rate', validators=[Optional()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

# === Product Deletion Form (Uses hidden product ID) ===
class DeleteForm(FlaskForm):
    delete_product = HiddenField('delete_product')

# === Product Editing Form (Pre-fills data with product ID) ===
class EditProductForm(FlaskForm):
    product_id = HiddenField('Product ID', default="-1")
    name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[DataRequired(), validate_expiry_date])
    units = IntegerField('Units', validators=[NumberRange(1, 30, "You can only upload from 1 to 30 units.")])
    price = FloatField('Price', validators=[DataRequired()])
    category = SelectField('Product Category', validators=[DataRequired()],
        choices=[
            ("f", "Fruits and Vegetables"),
            ("b", "Bakery"),
            ("d", "Dairy"),
            ("m", "Meat"),
            ("s", "Sweets"),
            ("r", "Ready to Eat")
        ])
    discount = FloatField('Discount Rate', validators=[Optional()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Update')

# === User Registration Form ===
class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# === Email Verification via OTP ===
class VerifyEmailForm(FlaskForm):
    otp = StringField('OTP code', validators=[DataRequired()])
    submit = SubmitField('Verify Email')

# === Password Reset Request Form ===
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

# === New Password Set Form After OTP Verification ===
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# === OTP Submission for Password Reset ===
class ResetOTPForm(FlaskForm):
    otp = StringField('OTP code', validators=[DataRequired()])
    submit = SubmitField('Verify OTP')

# === Password Change While Logged In ===
class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')
