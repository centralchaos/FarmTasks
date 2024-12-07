from flask import Flask, redirect, url_for, request
from app.extensions import db, login_manager
from app.utils import check_installation
import os
import secrets

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Generate a secure secret key if not exists
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    # Default configuration for initial setup
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///temp.db')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    
    # Try to load custom configuration from instance folder
    if os.path.exists(os.path.join(app.instance_path, 'config.py')):
        app.config.from_pyfile('config.py')
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    @app.before_request
    def check_installed():
        if not check_installation() and request.endpoint != 'installer.install':
            return redirect(url_for('installer.install'))
    
    from app.main import main as main_blueprint
    from app.installer import installer as installer_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(installer_blueprint)
    
    return app 