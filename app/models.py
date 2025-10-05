from datetime import datetime
from app import db, login_manager, bcrypt 
from flask_login import UserMixin
from config import Config

from itsdangerous import URLSafeTimedSerializer




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='technician') # or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')


    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)
    
    def get_reset_token(user_id, expires_sec=1800):
        s = URLSafeTimedSerializer(Config.SECRET_KEY)
        return s.dumps({'user_id': user_id})

    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(Config.SECRET_KEY)
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return user_id


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
    description = db.Column(db.Text)
    solution = db.Column(db.Text)
    # status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))   # e.g. Warehouse A - Shelf B
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<SparePart {self.name}>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey("spare_part.id"), nullable=False)
    machine_name = db.Column(db.String(120), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)
    date_used = db.Column(db.DateTime, default=datetime.utcnow)

    # Track who made the transaction
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    part = db.relationship("SparePart", backref="transactions", lazy=True)
    user = db.relationship("User", backref="transactions", lazy=True)


from datetime import datetime
from app import db

class ConsumableUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumable_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_used = db.Column(db.DateTime, default=datetime.utcnow)

    # relations
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # relationships
    machine = db.relationship("Machine", backref="consumables", lazy=True)
    user = db.relationship("User", backref="consumables", lazy=True)

    def __repr__(self):
        return f"<Consumable {self.consumable_name} - {self.quantity}>"
