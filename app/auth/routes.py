from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt 
from app.auth.forms import RegistrationForm, LoginForm , ResetPasswordForm , RequestResetForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

auth = Blueprint('auth', __name__, template_folder='templates/auth')




@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
    # check existing user
        if User.query.filter((User.username==form.username.data)|(User.email==form.email.data)).first():
            flash('Username or email already exists', 'danger')
            return render_template('auth/register.html', form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.home"))  # redirect logged-in users
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):  # uses User.check_password method
            login_user(user)
            flash("Login successful!", "success")

            # Redirect to next page if user tried to access a protected route
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("auth.home"))
        else:
            flash("Login failed. Please check your email and password.", "danger")

    return render_template("auth/login.html", form=form)


@auth.route('/home' , methods=['GET'])
def home():
    return render_template('main/home.html')


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))




def send_reset_email(user):
    token = User.get_reset_token(user.id)
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset Password', form=form)


@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user_id = User.verify_reset_token(token)
    if user_id is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    user = User.query.get(user_id)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_pw
        db.session.commit()
        print("done")
        flash('Your password has been updated! You can now log in', 'success')
        return redirect(url_for('auth.login'))
    # return render_template('auth/reset_token.html', title='Reset Password', form=form)
    return render_template("auth/reset_token.html", form=form, token=token)








