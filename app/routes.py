from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Task
from app import db
import requests

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.tasks'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('main.login'))
            
        login_user(user)
        return redirect(url_for('main.tasks'))
        
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/tasks')
@login_required
def tasks():
    # Obtener una frase motivacional
    try:
        response = requests.get('https://api.quotable.io/random')
        if response.status_code == 200:
            quote_data = response.json()
            quote = f'"{quote_data["content"]}" - {quote_data["author"]}'
        else:
            quote = "El éxito es la suma de pequeños esfuerzos repetidos día tras día."
    except:
        quote = "El éxito es la suma de pequeños esfuerzos repetidos día tras día."
    
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks, quote=quote)

@main.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    if title:
        task = Task(title=title, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('main.tasks'))

@main.route('/complete_task/<int:id>')
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for('main.tasks'))

@main.route('/delete_task/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('main.tasks'))