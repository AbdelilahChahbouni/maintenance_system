from flask import Blueprint, render_template, url_for, flash, redirect, request , jsonify
from app import db, bcrypt 
from app.auth.forms import RegistrationForm, LoginForm , ResetPasswordForm , DeleteUserForm ,RequestResetForm , UpdateAccountForm , ChangePasswordForm ,UpdateUserStatusForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from .utils import save_picture , create_jwt_token
from werkzeug.security import check_password_hash
from app import create_app






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
            print('Username or email already exists')
            return render_template('auth/register.html', form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You can now login.', 'success')
        print('Your account has been created. You can now login., success')
        return redirect(url_for('auth.login'))
    print('form not ok')
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET','POST'])
@auth.route('/', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))  # redirect logged-in users
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.status != 'active':
                flash("Your account is blocked. Contact admin.", "danger")
                return redirect(url_for('auth.blocked_user')) # uses User.check_password method
            login_user(user)
            flash("Login successful!", "success")

            # Redirect to next page if user tried to access a protected route
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
        else:
            flash("Login failed. Please check your email and password.", "danger")

    return render_template("auth/login.html", form=form)


@auth.route('/blocked_user' , methods=['GET'])
def blocked_user():
    return render_template('auth/blocked_user.html')

@auth.route('/account' , methods=['GET' , 'POST'])
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('auth/account.html', title='Account',
                           image_file=image_file, form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth.route('/users')
@login_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/list_users.html', users=users, title="User Management")


@auth.route('/admin/update_user_status', methods=['GET', 'POST'])
@login_required
def update_user_status():
    form = UpdateUserStatusForm()
    # Populate user select field with all users
    form.user.choices = [(u.id, u.username) for u in User.query.all()]

    if form.validate_on_submit():
        user = User.query.get(form.user.data)
        user.status = form.status.data
        db.session.commit()
        flash(f"{user.username} status updated to {user.status}", "success")
        return redirect(url_for('auth.update_user_status'))

    return render_template('auth/update_user_status.html', form=form, title='Update User Status')

@auth.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = DeleteUserForm()
    form.user.choices = [(u.id, f"{u.username} - {u.email}") for u in User.query.all()]

    if form.validate_on_submit():
        user_id = form.user.data
        user = User.query.get(user_id)

        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f"User '{user.username}' has been deleted successfully.", "success")
            return redirect(url_for('auth.list_users'))
        else:
            flash("User not found.", "danger")

    return render_template('auth/delete_user.html', form=form)




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



@auth.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        current_user.password_hash = hashed_pw
        db.session.commit()
        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('auth.account'))
    return render_template('auth/change_password.html', title='Change Password', form=form)



#API for login Phone App

 # if you already created token generator

@auth.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # Use model method
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # Create token
    token = create_jwt_token(user.id)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }), 200


