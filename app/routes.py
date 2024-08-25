from flask import Blueprint, render_template, request, redirect, url_for
from .conn import session, User, Ratings, User_preferences

main = Blueprint('main',__name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/entrar', methods=['POST'])
def logar():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('senha')
    else:
        return redirect(url_for('main.index'))
    
    usuario_existente = session.query(User).filter_by(email=email).first()
    
    if usuario_existente and password == usuario_existente.password:
        nome = usuario_existente.username
        
        return render_template('filmes.html', nome=nome)
    else:
        error = 'Email ou senha inválido'
        return render_template('index.html', error=error)
    