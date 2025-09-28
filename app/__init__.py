from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()




def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)


    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'


    # Blueprints
    from app.auth.routes import auth
    from app.main.routes import main
    from app.issues.routes import issues
    from app.consumables.routes import consumables


    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(issues)
    app.register_blueprint(consumables)


    return app