"""
Database models for the Farm Tasks application.
Contains models for Users, Tasks, Task Categories, Assignments and Templates.
"""

from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

class TaskCategory(db.Model):
    """Categories for organizing tasks"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TaskCategory {self.name}>'

class Task(db.Model):
    """Task model representing individual tasks"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_template = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('task_category.id'), nullable=True)
    priority = db.Column(db.String(20), default='medium')
    estimated_duration = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.relationship('TaskCategory', backref='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'

class TaskAssignment(db.Model):
    """Assignment of tasks to users with scheduling"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    task = db.relationship('Task')
    assignee = db.relationship('User')

    def __repr__(self):
        return f'<TaskAssignment {self.task.title} for {self.assignee.username}>'

class DayTemplate(db.Model):
    """Template for daily task schedules"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=False)
    assigned_date = db.Column(db.Date)
    task_assignments = db.relationship('DayTemplateTask', backref='day_template')

    @property
    def creator(self):
        """Get the user who created this template"""
        return User.query.get(self.created_by)

    @property
    def has_tasks(self):
        """Check if template has any tasks assigned"""
        return bool(self.task_assignments)

    @property
    def is_active(self):
        """Template is active when it has an assigned date"""
        return self.assigned_date is not None

    def duplicate(self):
        """Create a copy of this template"""
        new_template = DayTemplate(
            name=f"Copy of {self.name}",
            description=self.description,
            created_by=self.created_by
        )
        db.session.add(new_template)
        db.session.flush()

        for task in self.task_assignments:
            new_assignment = DayTemplateTask(
                day_template_id=new_template.id,
                task_id=task.task_id,
                user_id=task.user_id,
                scheduled_hour=task.scheduled_hour,
                scheduled_minute=task.scheduled_minute
            )
            db.session.add(new_assignment)

        return new_template

    def __repr__(self):
        return f'<DayTemplate {self.name}>'

class DayTemplateTask(db.Model):
    """Tasks within a day template"""
    id = db.Column(db.Integer, primary_key=True)
    day_template_id = db.Column(db.Integer, db.ForeignKey('day_template.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    scheduled_hour = db.Column(db.Integer)
    scheduled_minute = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Add relationship to User
    user = db.relationship('User', foreign_keys=[user_id])
    completed_by = db.relationship('User', foreign_keys=[completed_by_id])

    @property
    def task(self):
        """Get the associated task"""
        return Task.query.get(self.task_id)

    @property
    def completed_by(self):
        """Get the user who completed this task if any"""
        return User.query.get(self.completed_by_id) if self.completed_by_id else None

    def __repr__(self):
        return f'<DayTemplateTask {self.task.title} in {self.day_template.name}>'