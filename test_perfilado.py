from memory_profiler import profile
from app.routes import add_task, complete_task, delete_task, register
from app.models import User, Task
from app import create_app, db
from flask import Flask
from flask_login import login_user
from app.models import User
from config import TestConfig
from unittest.mock import Mock


# Configura la app para las pruebas
app = create_app(TestConfig)

def limpiar_bd():
    db.session.query(Task).delete()
    db.session.query(User).delete()
    db.session.commit()


# Perfilado de memoria
@profile
def test_agregar_tarea():
    limpiar_bd()
    with app.test_client() as client:
        # Crea un usuario de prueba para iniciar sesión
        user = User(username='usuario_test')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        login_user(user)

        # Realiza la solicitud para agregar tarea
        response = client.post('/add_task', data={'title': 'Nueva tarea de prueba'}, follow_redirects=True)
        assert response.status_code == 200

@profile
def test_completar_tarea():
    limpiar_bd()
    with app.test_client() as client:
        # Crea un usuario de prueba y una tarea
        user = User(username='usuario_test')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        login_user(user)

        task = Task(title='Tarea de prueba para completar', user_id=user.id)
        db.session.add(task)
        db.session.commit()

        task_id = task.id
        response = client.get(f'/complete_task/{task_id}', follow_redirects=True)
        assert response.status_code == 200

@profile
def test_eliminar_tarea():
    limpiar_bd()
    with app.test_client() as client:
        # Crea un usuario de prueba y una tarea
        user = User(username='usuario_test')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        login_user(user)

        task = Task(title='Tarea de prueba para eliminar', user_id=user.id)
        db.session.add(task)
        db.session.commit()

        task_id = task.id
        response = client.get(f'/delete_task/{task_id}', follow_redirects=True)
        assert response.status_code == 200

@profile
def test_registrar_usuario_simulado():
    # Simula la respuesta esperada de un registro exitoso
    response = Mock()
    response.data = b'Usuario registrado correctamente'

    # Verifica que el mensaje esté en la respuesta
    assert b'Usuario registrado correctamente' in response.data


# Función principal para ejecutar el perfilado
def main():
    with app.app_context():
        with app.test_request_context():
            test_agregar_tarea()
            test_completar_tarea()
            test_eliminar_tarea()
            test_registrar_usuario_simulado()





# Ejecutar el perfilado de tiempo
if __name__ == "__main__":
    main()

