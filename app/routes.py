from flask import Blueprint, render_template, request, redirect, url_for
from .conn import session, User, Ratings, User_preferences
from app.services import ApiFilmesService

main = Blueprint('main',__name__)
api_key = '32fca79cddd1530919c06027ce60b04e'
api_service = ApiFilmesService(api_key)

@main.route('/')
def index():
    return render_template('index.html')
# ---------------------- ROTAS DE AUTENTICAÇÃO E CADASTRO --------------------------------
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
        usuario_id = usuario_existente.user_id

        # Armazena o usuário na sessão
        session['usuario_id'] = usuario_id
        
        return render_template('filmes.html', nome=nome, email=email, usuario_id=usuario_id)
    else:
        error = 'Email ou senha inválido'
        return render_template('index.html', error=error)

@main.route('/cadastrar', methods=['POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome_cadastro')
        email = request.form.get('email_cadastro')
        senha = request.form.get('senha_cadastro')
        senhaConfirmada = request.form.get('confirm_senha')
        
        if senha == senhaConfirmada:
            if session.query(User).filter_by(email=email).first():
                error = 'Email já cadastrado'
                return render_template('index.html', error=error)
            
            novo_usuario = User(username=nome, email=email, password=senha)
            session.add(novo_usuario)
            session.commit()
            sucess = 'Usuário cadastrado com sucesso, faça seu login!'
            return redirect(url_for('main.index', sucess=sucess))
        else:
            error = 'Senhas não conferem'
            return redirect(url_for('main.index', error=error))
    
# ---------------------- ROTAS FILMES --------------------------------
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

# Rota de avaliação do filme
@main.route('/filme/avaliar/<int:id>', methods=['POST'])
def avaliar_filme(id):
    if request.method == 'POST':
        # Recebe a avaliação do formulário
        rating = request.form.get('rating')
        
        # Recupera o user_id da sessão
        usuario_id = session.get('usuario_id')
        
        # Identifica o id do filme
        movie_id = id
        
        # Verifica se o usuário já fez a avaliação deste filme
        avaliacao_existente = session.query(Ratings).filter_by(user_id=usuario_id, movie_id=movie_id).first()
        
        # Se não houver avaliação existente, adiciona uma nova
        if not avaliacao_existente:
            nova_avaliacao = Ratings(user_id=usuario_id, movie_id=movie_id, rating=rating)
            session.add(nova_avaliacao)
            session.commit()
        
        # Redireciona para a página do filme após a avaliação
        return redirect(url_for('main.get_filme', id=movie_id))

    