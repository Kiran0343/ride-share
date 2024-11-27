from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect





# Initialize extensions but do not bind to app yet
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf = CSRFProtect(app)
    csrf.init_app(app)
    app.config['WTF_CSRF_ENABLED'] = True

    # Bind extensions to app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.refresh_view = 'relogin'
    login_manager.needs_refresh_message = (u"Session timedout, please re-login")
    login_manager.needs_refresh_message_category = "info"

    from .models import User  # Import after db initialization to avoid circular imports


    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app
