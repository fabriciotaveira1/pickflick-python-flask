from flask import Blueprint, render_template, request, redirect, url_for
from .conn import session, User, Ratings, User_preferences
from app.services import ApiFilmesService

main = Blueprint('main',__name__)
api_key = '32fca79cddd1530919c06027ce60b04e'
api_service = ApiFilmesService(api_key)

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
        id = usuario_existente.user_id
        
        return render_template('filmes.html', nome=nome, email=email, id=id)
    else:
        error = 'Email ou senha inválido'
        return render_template('index.html', error=error)
    
@main.route('/pequisar', methods=['POST'])
def pesquisar():
    nome_filme = request.form.get('nome_filme')
    try:
        
        resultados = api_service.filtrar_filmes(nome_filme)
        return render_template('filmes.html', nome='', id='', resultados=resultados.get('results', []))
    except request.exceptions.HTTPError as e:
        return render_template('filmes.html', nome='', id='', error=f'Erro na requisição: {e}')
    
@main.route('/filme/<int:id>', methods=['GET'])
def get_filme(id):
    filme = api_service.get_filme_by_id(id)
    return render_template('filme.html', filme=filme)
    