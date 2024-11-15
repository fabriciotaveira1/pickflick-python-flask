from flask import Blueprint, render_template, request, redirect, url_for,jsonify, session as session_flask
from .conn import session, User, Ratings, User_preferences
from app.services import ApiFilmesService
from app.services import RecomendadorDeFilmesService

main = Blueprint('main',__name__)
api_key = '32fca79cddd1530919c06027ce60b04e'
api_service = ApiFilmesService(api_key)

# Inicialize o treinamento do modelo
recomendador = RecomendadorDeFilmesService()
recomendador.verificar_ou_treinar_modelo()

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
        session_flask['usuario_id'] = usuario_id

        return render_template('filmes.html', nome=nome, email=email, usuario_id=usuario_id)
    
    else:
        error = 'Email ou senha inválido'
        return render_template('index.html', error=error)


# Rota para retornar para a página filmes
@main.route('/filmes')
def filmes():
    nome = session_flask.get('nome')
    usuario_id = session_flask.get('usuario_id')


    return render_template('filmes.html', nome=nome, usuario_id=usuario_id)
    

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
        usuario_id = session_flask.get('usuario_id')
        
        # Identifica o id do filme
        movie_id = id

        # Se já existe uma avaliação, redireciona normalmente
        return redirect(url_for('main.filmes', id=movie_id))

    
# Rota para deletar avaliação do filme após a avaliação

@main.route('/filme/avaliar/<int:id>/deletar', methods=['POST'])
def deletar_avaliacao(id):
    if request.method == 'POST':
        # Recupera o user_id da sessão
        usuario_id = session_flask.get('usuario_id')
        
        # Recupera a avaliação do filme pelo id
        avaliacao = session.query(Ratings).filter_by(user_id=usuario_id, movie_api_id=id).first()
        
        # Verifica se a avaliação existe
        if avaliacao:
            # Deleta a avaliação
            session.delete(avaliacao)
            session.commit()
        
        # Redireciona para a página do filme após a deleção
        return redirect(url_for('main.get_filme', id=id))

# Rota para editar avaliação do filme

@main.route('/filme/avaliar/<int:id>/editar', methods=['POST'])
def editar_avaliacao(id):
    if request.method == 'POST':
        # Recebe a nova avaliação do formulário
        rating = request.form.get('rating')
        
        # Recupera o user_id da sessão
        usuario_id = session_flask.get('usuario_id')
        
        # Recupera a avaliação do filme pelo id
        avaliacao = session.query(Ratings).filter_by(user_id=usuario_id, movie_api_id=id).first()
        
        # Verifica se a avaliação existe
        if avaliacao:
            # Atualiza a avaliação
            avaliacao.rating = rating
            session.commit()
        
        # Redireciona para a página do filme após a edição
        return redirect(url_for('main.get_avaliacoes', id=id))

# Rota para visualizar todas as avaliações

@main.route('/avaliacoes')
def get_avaliacoes():
    # Recupera o user_id da sessão
    usuario_id = session_flask.get('usuario_id')
    
    # Recupera as avaliações do filme pelo user_id
    avaliacoes = session.query(Ratings).filter_by(user_id=usuario_id).all()
    
    try:
        # Recupera os filmes das avaliações
        filmes = [api_service.get_filme_by_id(avaliacao.movie_api_id) for avaliacao in avaliacoes]
        
        return render_template('avaliacoes.html', avaliacoes=avaliacoes, filmes=filmes, zip=zip)
    except:
        error = 'Erro ao buscar avaliações'
        return render_template('avaliacoes.html', avaliacoes=avaliacoes, error=error, zip=zip)

@main.route('/recomendar', methods=['GET'])
def recomendar():
    usuario_id = request.args.get('usuario_id', type=int)
    if not usuario_id:
        return jsonify({'error': 'Usuário ID não fornecido'}), 400

    recomendacoes = recomendador.recomendar_filmes_hibrido(usuario_id)
    
    return jsonify(recomendacoes)
