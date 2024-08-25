# __init.py__ - Inicializa a aplicação flask

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'w6wLfcK57QTZWZ@#QFTg77'
    
    from .routes import main
    app.register_blueprint(main)
    
    return app