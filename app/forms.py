import datetime

from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange


class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class InventoryForm(FlaskForm):
    edit = HiddenField ('Edit',default = "-1")
    name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])
    units = IntegerField('Units', validators= [NumberRange(1,30, "You can only upload from 1 to 30 units.")])
    price = FloatField('Price', validators= [DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_expiry_date(self, field):
        today = datetime.date.today()  # get today's date (no time part)
        expiry_date = field.data       # field.data is already a date (because you're using DateField)

        if expiry_date < today:
            raise ValidationError("You can't upload expired goods!")

class DeleteForm(FlaskForm):
    delete_product = HiddenField('delete_product')

class EditProductForm(FlaskForm):
    edit_product = HiddenField('edit_product')
