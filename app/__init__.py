from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from flask_mail import Mail
import os
from dotenv import load_dotenv




db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'djangotest2025@gmail.com'
    app.config['MAIL_PASSWORD'] = 'mkfg xorp pnqr budw'
    mail.init_app(app)


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)


    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'


    # Blueprints
    from app.auth.routes import auth
    # from app.main.routes import main
    from app.issues.routes import issues
    # from app.consumables.routes import consumables


    app.register_blueprint(auth)
    # app.register_blueprint(main)
    app.register_blueprint(issues)
    # app.register_blueprint(consumables)


    return app