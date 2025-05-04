import pytest
from app import create_app, db
from app.models import User, Task
from unittest.mock import patch, MagicMock
import uuid

# Esta función ayuda a generar nombres de usuario únicos para evitar conflictos
def generate_unique_username():
    return f"testuser_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test_key'
    })
    
    # Configuramos el contexto de aplicación
    app.app_context().push()
    
    # Creamos las tablas
    db.create_all()
    
    yield app
    
    # Limpiamos después de cada prueba
    db.session.remove()
    db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    username = generate_unique_username()
    user = User(username=username)
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    client.post('/login', data={
        'username': test_user.username,
        'password': 'testpassword'
    }, follow_redirects=True)
    return client

def test_crear_usuario():
    """Prueba la creación de un usuario y el método set_password"""
    user = User(username='usuario_nuevo')
    user.set_password('contraseña123')
    
    assert user.username == 'usuario_nuevo'
    assert user.password_hash is not None
    assert user.password_hash != 'contraseña123'  # Verifica que se haya hasheado la contraseña

def test_verificar_contraseña():
    """Prueba el método check_password"""
    user = User(username='usuario_test')
    user.set_password('contraseña123')
    
    assert user.check_password('contraseña123') is True
    assert user.check_password('contraseña_incorrecta') is False

def test_crear_tarea(app, test_user):
    """Prueba la creación de una tarea asociada a un usuario"""
    task = Task(title='Tarea de prueba', user_id=test_user.id)
    db.session.add(task)
    db.session.commit()
    
    saved_task = Task.query.filter_by(title='Tarea de prueba').first()
    assert saved_task is not None
    assert saved_task.title == 'Tarea de prueba'
    assert saved_task.completed is False
    assert saved_task.user_id == test_user.id

def test_login_exitoso(client, test_user):
    """Prueba un inicio de sesión exitoso"""
    response = client.post('/login', data={
        'username': test_user.username,
        'password': 'testpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Mis Tareas' in response.data or b'tasks' in response.data  # Ajusta según tu HTML

def test_login_fallido(client, test_user):
    """Prueba un inicio de sesión fallido"""
    response = client.post('/login', data={
        'username': test_user.username,
        'password': 'contraseña_incorrecta'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Usuario o contraseña incorrectos' in response_text

def test_logout(authenticated_client):
    """Prueba la funcionalidad de cierre de sesión"""
    response = authenticated_client.get('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    # Verifica que estés en la página de login después de cerrar sesión
    response_text = response.data.decode('utf-8')
    assert 'login' in response_text.lower() or 'iniciar sesión' in response_text.lower()

def test_agregar_tarea(authenticated_client, app):
    """Prueba la funcionalidad de agregar una nueva tarea"""
    task_title = f"Nueva tarea {uuid.uuid4().hex[:8]}"
    response = authenticated_client.post('/add_task', data={
        'title': task_title
    }, follow_redirects=True)
    
    assert response.status_code == 200
    task = Task.query.filter_by(title=task_title).first()
    assert task is not None

def test_completar_tarea(authenticated_client, test_user):
    """Prueba la funcionalidad de marcar una tarea como completada"""
    # Crear una tarea para el usuario autenticado
    task = Task(title='Tarea para completar', user_id=test_user.id)
    db.session.add(task)
    db.session.commit()
    task_id = task.id
    
    # Cambiar estado de la tarea
    response = authenticated_client.get(f'/complete_task/{task_id}', follow_redirects=True)
    
    assert response.status_code == 200
    updated_task = Task.query.get(task_id)
    assert updated_task.completed is True

@patch('requests.get')
def test_obtener_frase_motivacional(mock_get, authenticated_client):
    """Prueba la obtención de una frase motivacional externa"""
    # Simulamos la respuesta de la API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": "La vida es lo que hacemos de ella",
        "author": "Autor Test"
    }
    mock_get.return_value = mock_response
    
    response = authenticated_client.get('/tasks', follow_redirects=True)
    
    assert response.status_code == 200
    # Verificamos que la frase aparezca en la página
    # Puedes ajustar esta verificación según el formato exacto de tu HTML
    assert b'La vida es lo que hacemos de ella' in response.data or b'Autor Test' in response.data
    mock_get.assert_called_once_with('https://api.quotable.io/random')

def test_eliminar_tarea(authenticated_client, test_user):
    """Prueba la funcionalidad de eliminar una tarea"""
    # Crear una tarea para el usuario autenticado
    task = Task(title='Tarea para eliminar', user_id=test_user.id)
    db.session.add(task)
    db.session.commit()
    task_id = task.id
    
    # Eliminar la tarea
    response = authenticated_client.get(f'/delete_task/{task_id}', follow_redirects=True)
    
    assert response.status_code == 200
    deleted_task = Task.query.get(task_id)
    assert deleted_task is None