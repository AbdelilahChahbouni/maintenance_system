# app/admin.py
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        # Only allow access if the user is authenticated and is admin
        return current_user.is_authenticated and current_user.role == "technician"

    def inaccessible_callback(self, name, **kwargs):
        # Redirect or flash message if unauthorized
        print('Redirect or flash message if unauthorized')
        from flask import redirect, url_for, flash
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("auth.login"))
