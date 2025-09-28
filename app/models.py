from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='technician') # or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def set_password(self, password, bcrypt):
    self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(self, password, bcrypt):
    return bcrypt.check_password_hash(self.password_hash, password)


def __repr__(self):
    return f"<User {self.username}>"




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# Placeholder models for shell context and later weeks
class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    machine_name = db.Column(db.String(100))
    # description = db.Column(db.Text)
    solution = db.Column(db.text)
    # status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)


class StockTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id'))
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class ConsumableUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id'))
    quantity_used = db.Column(db.Integer)
    machine_name = db.Column(db.String(100))
    date_used = db.Column(db.DateTime, default=datetime.utcnow)