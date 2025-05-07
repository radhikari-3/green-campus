import datetime

from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField
from wtforms.fields import DateField
from wtforms.fields import IntegerField, FloatField
from wtforms.fields import SelectField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.validators import Email, EqualTo
from wtforms.validators import ValidationError


def validate_expiry_date(self, field):
    today = datetime.date.today()   # get today's date (no time part)
    if field.data < today:          # field.data is already a date (because you're using DateField)
        raise ValidationError("You can't upload expired goods!")

class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[DataRequired(), validate_expiry_date])
    units = IntegerField('Units', validators=[NumberRange(1, 30, "You can only upload from 1 to 30 units.")])
    price = FloatField('Price', validators=[DataRequired()])
    category = SelectField('Product Category', validators=[DataRequired()],
                           choices=[("f", "Fruits and Vegetables"), ("b", "Bakery"),
                                    ("d", "Dairy"), ("m", "Meat"), ("s", "Sweets"), ("r", "Ready to Eat")])
    discount = FloatField('Discount Rate', validators=[Optional()])  # Ensure no required validators
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    delete_product = HiddenField('delete_product')

class EditProductForm(FlaskForm):
    product_id = HiddenField('Product ID', default="-1")
    name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[DataRequired(), validate_expiry_date])
    units = IntegerField('Units', validators=[NumberRange(1, 30, "You can only upload from 1 to 30 units.")])
    price = FloatField('Price', validators=[DataRequired()])
    category = SelectField('Product Category', validators=[DataRequired()],
                           choices=[("f", "Fruits and Vegetables"), ("b", "Bakery"),
                                    ("d", "Dairy"), ("m", "Meat"), ("s", "Sweets"), ("r", "Ready to Eat")])
    discount = FloatField('Discount Rate', validators=[Optional()])  # Ensure no required validators
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Update')

class SignupForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit   = SubmitField('Sign Up')

class VerifyEmailForm(FlaskForm):
    otp    = StringField('OTP code', validators=[DataRequired()])
    submit = SubmitField('Verify Email')

class ResetPasswordRequestForm(FlaskForm):
    email  = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password  = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit    = SubmitField('Reset Password')

class ResetOTPForm(FlaskForm):
    otp = StringField('OTP code', validators=[DataRequired()])
    submit = SubmitField('Verify OTP')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password',     validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')



