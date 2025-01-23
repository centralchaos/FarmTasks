"""Database initialization script"""
from app import create_app, db
from app.models import User, TaskCategory

def init_db():
    """Initialize the database with required data"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        if not User.query.filter_by(role='admin').first():
            # Create default admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin')  # Set a default password
            db.session.add(admin)
            
            # Create default task categories
            default_categories = ['Daily', 'Weekly', 'Monthly', 'Special']
            for category_name in default_categories:
                category = TaskCategory(name=category_name)
                db.session.add(category)
            
            db.session.commit()

if __name__ == '__main__':
    init_db() 