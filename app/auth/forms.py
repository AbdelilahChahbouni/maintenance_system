from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User




class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(2, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


# validation functions are implemented in the route to avoid circular import

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password' , validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password' , validators=[DataRequired() , EqualTo('password')])
    submit = SubmitField('Reset Password')

class RequestResetForm(FlaskForm):
     email = StringField('Email' , validators=[DataRequired() , Email()])
     submit = SubmitField('Reset Password')
     def validate_email(self , email):
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                 raise ValidationError("There is no Account with that email , You musst register first")
