from flask import render_template, redirect, url_for, flash, request, current_app
from app.installer import installer
from app import db
from app.models import User
from app.utils import check_installation
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
import secrets
import time

@installer.route('/install', methods=['GET', 'POST'])
def install():
    """Installation wizard"""
    # Add debug logging
    current_app.logger.info("Checking installation status...")
    
    # Check if config exists but database is not accessible
    if os.path.exists(os.path.join(current_app.instance_path, 'config.py')):
        current_app.logger.info("Config file exists, checking database...")
        if not check_installation():
            current_app.logger.error("Database not accessible despite config existing")
            flash("Database configuration exists but database is not accessible", "error")
    
    if request.method == 'POST':
        step = request.form.get('step', '1')
        
        if step == '1':  # Database configuration
            try:
                # Build database URL
                db_type = request.form['db_type']
                db_user = request.form['db_user']
                db_pass = request.form['db_password']
                db_host = request.form['db_host']
                db_name = request.form['db_name']
                
                if db_type == 'sqlite':
                    db_url = f'sqlite:///{db_name}.db'
                else:
                    db_url = f'{db_type}://{db_user}:{db_pass}@{db_host}/{db_name}'
                
                # Test connection
                engine = create_engine(db_url)
                engine.connect()
                
                # Generate a secure secret key
                secret_key = secrets.token_hex(32)
                
                # Save configuration
                config_path = os.path.join(current_app.instance_path, 'config.py')
                with open(config_path, 'w') as f:
                    f.write(f"SQLALCHEMY_DATABASE_URI = '{db_url}'\n")
                    f.write("SQLALCHEMY_TRACK_MODIFICATIONS = False\n")
                    f.write(f"SECRET_KEY = '{secret_key}'\n")
                
                # Create all tables immediately after saving config
                db.create_all()
                current_app.logger.info("Database tables created successfully")
                
                return render_template('installer/step2.html')
                
            except Exception as e:
                flash(f'Database configuration error: {str(e)}', 'error')
                return render_template('installer/step1.html')
        
        elif step == '2':  # Admin account creation
            try:
                # Create admin user
                admin = User(
                    username=request.form['username'],
                    email=request.form['email'],
                    role='admin'
                )
                admin.set_password(request.form['password'])
                
                db.session.add(admin)
                
                # Create default task categories
                from app.models import TaskCategory
                default_categories = ['Daily', 'Weekly', 'Monthly', 'Special']
                for category_name in default_categories:
                    category = TaskCategory(name=category_name)
                    db.session.add(category)
                
                db.session.commit()
                current_app.logger.info("Admin user and default categories created successfully")
                
                flash('Installation completed successfully!')
                return redirect(url_for('main.login'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating admin account: {str(e)}', 'error')
                return render_template('installer/step2.html')
    
    return render_template('installer/step1.html') 

