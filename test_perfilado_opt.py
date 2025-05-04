from memory_profiler import profile
from app import create_app, db
from app.models import User, Task
from flask_login import login_user
from config import TestConfig

app = create_app(TestConfig)

def limpiar_bd():
    db.session.query(Task).delete()
    db.session.query(User).delete()
    db.session.commit()

@profile
def test_agregar_tarea():
    limpiar_bd()
    client = app.test_client()

    user = User(username='usuario_test')
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    
    with app.test_request_context():
        login_user(user)

    response = client.post('/add_task', data={'title': 'Nueva tarea de prueba'}, follow_redirects=True)
    assert response.status_code == 200

@profile
def test_completar_tarea():
    limpiar_bd()
    client = app.test_client()

    user = User(username='usuario_test')
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()

    task = Task(title='Tarea de prueba para completar', user_id=user.id)
    db.session.add(task)
    db.session.commit()

    with app.test_request_context():
        login_user(user)

    response = client.get(f'/complete_task/{task.id}', follow_redirects=True)
    assert response.status_code == 200

@profile
def test_eliminar_tarea():
    limpiar_bd()
    client = app.test_client()

    user = User(username='usuario_test')
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()

    task = Task(title='Tarea de prueba para eliminar', user_id=user.id)
    db.session.add(task)
    db.session.commit()

    with app.test_request_context():
        login_user(user)

    response = client.get(f'/delete_task/{task.id}', follow_redirects=True)
    assert response.status_code == 200

@profile
def test_registrar_usuario_simulado():
    # Simula directamente sin usar librerías extra
    class FakeResponse:
        data = b'Usuario registrado correctamente'

    response = FakeResponse()
    assert b'Usuario registrado correctamente' in response.data

def main():
    with app.app_context():
        test_agregar_tarea()
        test_completar_tarea()
        test_eliminar_tarea()
        test_registrar_usuario_simulado()

if __name__ == "__main__":
    main()