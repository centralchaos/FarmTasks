"""Utility functions for the Farm Tasks application"""
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.extensions import db
from app.models import User
from flask import current_app
import os

def is_db_configured():
    """Check if database is configured and accessible"""
    try:
        # Try to connect to the database and perform a simple query
        with db.engine.connect() as conn:
            conn.execute(db.text("SELECT 1"))
        current_app.logger.info("Database connection successful")
        return True
    except Exception as e:
        current_app.logger.error(f"Database connection failed: {str(e)}")
        return False

def is_app_initialized():
    """Check if application is initialized (has admin user)"""
    try:
        # Use a session to ensure proper connection handling
        with db.session.begin():
            has_admin = bool(User.query.filter_by(role='admin').first())
            current_app.logger.info(f"Admin user check: {'found' if has_admin else 'not found'}")
            return has_admin
    except Exception as e:
        current_app.logger.error(f"Admin check failed: {str(e)}")
        return False

def check_installation():
    """Check if application needs installation"""
    try:
        # Check if config exists in instance folder
        config_path = os.path.join(current_app.instance_path, 'config.py')
        if not os.path.exists(config_path):
            current_app.logger.info("No config file found")
            return False
            
        # Try to connect and verify tables exist
        with db.engine.connect() as conn:
            # Check if admin user exists
            result = conn.execute(db.text("SELECT COUNT(*) FROM user WHERE role = 'admin'"))
            has_admin = result.scalar() > 0
            
            if not has_admin:
                current_app.logger.info("No admin user found")
                return False
                
            current_app.logger.info("Installation verified: config exists and admin user found")
            return True
            
    except Exception as e:
        current_app.logger.error(f"Installation check error: {str(e)}")
        return False