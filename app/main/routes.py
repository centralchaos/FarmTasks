from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main
from app.models import User, Task, TaskAssignment, DayTemplate, DayTemplateTask, TaskCategory
from app.extensions import db
from datetime import datetime, date, time
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
@login_required
def dashboard():
    today = date.today()
    tasks = TaskAssignment.query.filter_by(
        user_id=current_user.id,
        scheduled_date=today
    ).all()
    
    # Get all templates with assigned dates
    templates = DayTemplate.query.filter(DayTemplate.assigned_date.isnot(None)).all()
    templates_json = [{
        'id': t.id,
        'name': t.name,
        'assigned_date': t.assigned_date.strftime('%Y-%m-%d') if t.assigned_date else None
    } for t in templates]
    
    return render_template('dashboard.html', 
                         tasks=tasks,
                         templates=templates_json)  # Pass the JSON-serializable list

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@main.route('/tasks', methods=['GET', 'POST'])
@login_required
@admin_required
def tasks():
    if request.method == 'POST':
        task = Task(
            title=request.form['title'],
            description=request.form['description'],
            is_template=True
        )
        db.session.add(task)
        db.session.commit()
        flash('Task template created successfully')
    
    tasks = Task.query.filter_by(is_template=True).all()
    users = User.query.filter_by(role='user').all()
    return render_template('tasks/list.html', tasks=tasks, users=users)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    """Manage system users"""
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already exists', 'error')
            return redirect(url_for('main.manage_users'))
            
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already exists', 'error')
            return redirect(url_for('main.manage_users'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            role=request.form['role']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('User created successfully')
        return redirect(url_for('main.manage_users'))
    
    users = User.query.all()
    return render_template('users.html', users=users)

@main.route('/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account')
        return redirect(url_for('main.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('main.manage_users'))

@main.route('/day_templates', methods=['GET', 'POST'])
@login_required
def day_templates():
    if request.method == 'POST':
        # Only admin can create templates
        if not current_user.is_admin():
            abort(403)
            
        name = request.form['name']
        description = request.form['description']
        
        template = DayTemplate(
            name=name,
            description=description,
            created_by=current_user.id
        )
        db.session.add(template)
        db.session.commit()
        flash('Day template created successfully')
        return redirect(url_for('main.edit_day_template', template_id=template.id))
    
    templates = DayTemplate.query.all()
    users = User.query.all()
    return render_template('day_templates/index.html', 
                         templates=templates, 
                         users=users,
                         is_admin=current_user.is_admin())

@main.route('/day_templates/<int:template_id>', methods=['GET', 'POST'])
@login_required
def edit_day_template(template_id):
    template = DayTemplate.query.get_or_404(template_id)
    tasks = Task.query.filter_by(is_template=True).all()
    users = User.query.all()
    
    if request.method == 'POST':
        # Only admin can modify templates
        if not current_user.is_admin():
            abort(403)
            
        task_id = request.form['task_id']
        hour = int(request.form['hour'])
        minute = int(request.form.get('minute', 0))
        user_id = request.form.get('user_id')
        
        task_assignment = DayTemplateTask(
            day_template_id=template.id,
            task_id=task_id,
            user_id=user_id if user_id else None,
            scheduled_hour=hour,
            scheduled_minute=minute
        )
        db.session.add(task_assignment)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success'}
            
        flash('Task added to template')
        return redirect(url_for('main.edit_day_template', template_id=template.id))
    
    return render_template('day_templates/edit.html', 
                         template=template, 
                         tasks=tasks, 
                         users=users,
                         is_admin=current_user.is_admin()) 

@main.route('/day_templates/bulk_delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete_templates():
    template_ids = request.form.getlist('template_ids[]')
    deleted_count = 0
    error_count = 0
    
    try:
        for template_id in template_ids:
            template = DayTemplate.query.get_or_404(int(template_id))
            
            # Check if template has tasks assigned
            if template.task_assignments:
                flash(f'Cannot delete template "{template.name}": Has assigned tasks', 'error')
                error_count += 1
                continue
                
            try:
                db.session.delete(template)
                deleted_count += 1
            except Exception as e:
                db.session.rollback()
                flash(f'Error deleting template "{template.name}": {str(e)}', 'error')
                error_count += 1
                
        if deleted_count > 0:
            db.session.commit()
            flash(f'Successfully deleted {deleted_count} template(s)')
            
        if error_count > 0:
            flash(f'Failed to delete {error_count} template(s)', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error during bulk delete: {str(e)}', 'error')
    
    return redirect(url_for('main.day_templates'))

@main.route('/day_templates/bulk_duplicate', methods=['POST'])
@login_required
@admin_required
def bulk_duplicate_templates():
    template_ids = request.form.getlist('template_ids[]')
    
    try:
        for template_id in template_ids:
            template = DayTemplate.query.get_or_404(int(template_id))
            new_template = template.duplicate()
        
        db.session.commit()
        flash('Selected templates duplicated successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error duplicating templates', 'error')
    
    return redirect(url_for('main.day_templates')) 

@main.route('/day_templates/<int:template_id>/apply', methods=['POST'])
@login_required
@admin_required
def apply_day_template(template_id):
    template = DayTemplate.query.get_or_404(template_id)
    date_str = request.form['date']
    user_id = request.form['user_id']
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Set the assigned date for the template
        template.assigned_date = target_date
        
        # Create task assignments
        assignments_created = 0
        for template_task in template.task_assignments:
            scheduled_time = time(hour=template_task.scheduled_hour, 
                                minute=template_task.scheduled_minute)
            
            assignment = TaskAssignment(
                task_id=template_task.task_id,
                user_id=user_id,
                scheduled_date=target_date,
                scheduled_time=scheduled_time
            )
            db.session.add(assignment)
            assignments_created += 1
        
        db.session.commit()
        flash(f'Day template applied successfully. Created {assignments_created} task assignments.')
    except ValueError as e:
        flash(f'Error: {str(e)}', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error applying template: {str(e)}', 'error')
    
    return redirect(url_for('main.day_templates')) 

@main.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_task(task_id):
    """Edit an existing task template"""
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        try:
            # Convert estimated_duration to integer if provided and not empty
            duration = request.form.get('estimated_duration')
            duration = int(duration) if duration and duration.strip() else None
            
            # Get category_id if provided and not empty
            category_id = request.form.get('category_id')
            category_id = int(category_id) if category_id and category_id.strip() else None
            
            # Update task fields
            task.title = request.form['title']
            task.description = request.form.get('description', '')
            task.category_id = category_id
            task.priority = request.form.get('priority', 'medium')
            task.estimated_duration = duration
            
            db.session.commit()
            flash('Task updated successfully')
            return redirect(url_for('main.tasks'))
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Invalid input: {str(e)}', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'error')
    
    categories = TaskCategory.query.all()
    return render_template('tasks/edit.html', task=task, categories=categories)

@main.route('/day_templates/<int:template_id>/edit_details', methods=['POST'])
@login_required
@admin_required
def edit_template_details(template_id):
    """Edit day template details"""
    template = DayTemplate.query.get_or_404(template_id)
    
    template.name = request.form['name']
    template.description = request.form.get('description')
    
    # Handle assigned date
    assigned_date = request.form.get('assigned_date')
    if assigned_date:
        template.assigned_date = datetime.strptime(assigned_date, '%Y-%m-%d').date()
    else:
        template.assigned_date = None
    
    db.session.commit()
    flash('Template details updated successfully')
    return redirect(url_for('main.edit_day_template', template_id=template.id)) 

@main.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_task(task_id):
    """Delete a task template"""
    task = Task.query.get_or_404(task_id)
    
    # Check if task is used in any day templates
    template_assignments = DayTemplateTask.query.filter_by(task_id=task_id).first()
    if template_assignments:
        flash('Cannot delete task: It is being used in one or more day templates', 'error')
        return redirect(url_for('main.tasks'))
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting task', 'error')
    
    return redirect(url_for('main.tasks')) 

@main.route('/day_templates/complete_task/<int:assignment_id>', methods=['POST'])
@login_required
def complete_template_task(assignment_id):
    """Complete a task in a day template"""
    assignment = DayTemplateTask.query.get_or_404(assignment_id)
    
    # Check if the user is assigned to this task or is admin
    if assignment.user_id == current_user.id or current_user.is_admin():
        assignment.completed = True
        assignment.completed_at = datetime.utcnow()
        assignment.completed_by_id = current_user.id
        db.session.commit()
        flash('Task marked as complete')
    else:
        flash('You are not authorized to complete this task', 'error')
    
    # Redirect back to the day template view
    return redirect(url_for('main.edit_day_template', template_id=assignment.day_template_id)) 