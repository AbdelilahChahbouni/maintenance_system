from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.access_denied'))

    # Hide internal or auto fields
    form_excluded_columns = ['password_hash', 'issues', 'created_at']

    # Optional: add nice labels
    column_labels = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'username': 'Username',
        'email': 'Email',
        'role': 'Role',
        'image_file': 'Profile Image'
    }

    # Optional: restrict which columns are visible in list view
    column_list = ['id', 'username', 'email', 'role', 'created_at']

    # Optional: add a dropdown for roles
    form_choices = {
        'role': [
            ('admin', 'Admin'),
            ('technician', 'Technician'),
            ('user', 'User')
        ]
    }
