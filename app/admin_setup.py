from flask import redirect, url_for, abort, request
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app import db
from app.models import User, Machine, Issue, SparePart, Transaction


# ✅ Custom Admin Home page (prevents access before loading layout)
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'technician'

    def inaccessible_callback(self, name, **kwargs):
        # Redirect BEFORE rendering any HTML
        return redirect(url_for('main.access_denied'))


# ✅ Custom model view (for all models)
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'technician'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.access_denied'))


def create_admin(app):
    admin = Admin(app, name='Maintenance Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())

    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Machine, db.session))
    admin.add_view(AdminModelView(Issue, db.session))
    admin.add_view(AdminModelView(SparePart, db.session))
    admin.add_view(AdminModelView(Transaction, db.session))
