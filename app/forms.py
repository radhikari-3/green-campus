import datetime

from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange, ValidationError, InputRequired

from wtforms.validators import DataRequired, Email, EqualTo

class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class InventoryForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])
    units = IntegerField('Units', validators= [NumberRange(1,30, "You can only upload from 1 to 30 units.")])
    marked_price = FloatField('Marked Price', validators= [DataRequired()])
    discount = FloatField('Discount Rate', validators=[InputRequired()])
    category = SelectField('Product Category', validators=[DataRequired()], choices=[("f","fruits and vegetables"),("g","grains"),("d","dairy and related products"),("n","nuts")])
    location = StringField('Product location', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_expiry_date(self, field):
        today = datetime.date.today()  # get today's date (no time part)
        expiry_date = field.data       # field.data is already a date (because you're using DateField)

        if expiry_date < today:
            raise ValidationError("You can't upload expired goods!")

    def validate_discount(self, field):
        discount = field.data
        if float(discount) > 100 or float(discount) < 0:
            raise ValidationError("The discount rate should be a numerical value between 0-100")


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




