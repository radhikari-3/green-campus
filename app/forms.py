from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

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




