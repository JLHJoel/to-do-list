class Config:
    SECRET_KEY = 'clave-secreta-muy-segura'
    # Aquí usamos SQLite para simplificar
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False