from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.extensions import db, login_manager
import os
import logging

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Add debug logging
    app.logger.setLevel(logging.DEBUG)
    
    # Configure from environment variables
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.logger.debug(f"Using database URI: {db_uri}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    
    try:
        # Initialize extensions
        db.init_app(app)
        with app.app_context():
            # Test database connection
            db.engine.connect()
            app.logger.debug("Database connection successful")
    except Exception as e:
        app.logger.error(f"Database connection failed: {str(e)}")
        raise
    
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app 