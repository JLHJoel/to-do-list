
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import random

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
    
    return app


from flask import current_app

@db.event.listens_for(db.engine, "connect")
def inject_random_id(*args, **kwargs):
    current_app.jinja_env.globals['random_id'] = random.randint(1, 10000)
