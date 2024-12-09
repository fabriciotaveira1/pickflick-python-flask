from flask import Blueprint, render_template, request, redirect, url_for,jsonify, session as session_flask
from .conn import session, User, Ratings
from app.services import ApiFilmesService
from app.services import RecomendadorDeFilmesService
import pandas as pd
import bcrypt

main = Blueprint('main',__name__)
api_key = '32fca79cddd1530919c06027ce60b04e'
api_service = ApiFilmesService(api_key)

# Inicialize o treinamento do modelo
recomendador = RecomendadorDeFilmesService()
recomendador.verificar_ou_treinar_modelo()

@main.route('/')
def index():
    return render_template('index.html')

# ---------------------- ROTAS DE AUTENTICAÇÃO E CADASTRO --------------------------------@main.route('/entrar', methods=['POST'])
@main.route('/entrar', methods=['POST'])
def logar():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('senha').strip()  # Remove espaços desnecessários
    else:
        return redirect(url_for('main.index'))

    # Verifica se o usuário existe
    usuario_existente = session.query(User).filter_by(email=email).first()
    
    if usuario_existente:
        print(f"Senha inserida pelo usuário: {password}")
        print(f"Hash do banco de dados: {usuario_existente.password}")

        # Verifica se a senha está correta
        if bcrypt.checkpw(password.encode('utf-8'), usuario_existente.password.encode('utf-8')):
            nome = usuario_existente.username
            usuario_id = usuario_existente.user_id
            session_flask['usuario_id'] = usuario_id

            # Recupera as avaliações do filme pelo user_id
            avaliacoes = session.query(Ratings).filter_by(user_id=usuario_id).all()

            # Buscar as avaliações do banco de dados
            avaliacoes_usuario = [
                {
                    'movie_api_id': avaliacao.movie_api_id,
                    'rating': avaliacao.rating
                }
                for avaliacao in avaliacoes
            ]
            recomendacoes_ids = recomendador.recomendar_filmes_hibrido(usuario_id, avaliacoes_usuario)
            
            # Agora, obtemos os detalhes dos filmes recomendados usando o método da API
            filmes_recomendados = []
            for recomendacao in recomendacoes_ids:
                filme = recomendacao
                filmes_recomendados.append(filme)

            # Renderiza a página de filmes com os filmes recomendados
            return render_template('filmes.html', nome=nome, email=email, usuario_id=usuario_id, filmes_recomendados=filmes_recomendados)
    
    error = 'Email ou senha inválido'
    return render_template('index.html', error=error)


#rota para sair e encerrar sessão
@main.route('/sair')
def sair():
    session_flask.clear()
    return redirect(url_for('main.index'))

# Rota para retornar para a página filmes
@main.route('/filmes')
def filmes():
    nome = session_flask.get('nome')
    usuario_id = session_flask.get('usuario_id')
    
    try:
        # Recupera as avaliações do filme pelo user_id
        avaliacoes = session.query(Ratings).filter_by(user_id=usuario_id).all()

        # Buscar as avaliações do banco de dados
        avaliacoes_usuario = [
            {
                'movie_api_id': avaliacao.movie_api_id,
                'rating': avaliacao.rating
            }
            for avaliacao in avaliacoes
        ]
        recomendacoes_ids = recomendador.recomendar_filmes_hibrido(usuario_id, avaliacoes_usuario)
        
        # Agora, obtemos os detalhes dos filmes recomendados usando o método da API
        filmes_recomendados = []
        for recomendacao in recomendacoes_ids:
            filme = recomendacao
            filmes_recomendados.append(filme)
        
        # Renderiza a página de filmes com os filmes recomendados
        return render_template('filmes.html', nome=nome, usuario_id=usuario_id, filmes_recomendados=filmes_recomendados)
    except Exception as e:
        return render_template('filmes.html', nome=nome, usuario_id=usuario_id, error=f'Erro ao recuperar filmes recomendados: {e}')
    
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
            
            # Hashear a senha
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Criar o novo usuário
            novo_usuario = User(username=nome, email=email, password=senha_hash)
            session.add(novo_usuario)
            session.commit()
            sucess = 'Usuário cadastrado com sucesso, faça seu login!'
            return redirect(url_for('main.index', sucess=sucess))
        else:
            error = 'Senhas não conferem'
            return redirect(url_for('main.index', error=error))
    
# ---------------------- ROTAS FILMES --------------------------------
@main.route('/pesquisar', methods=['POST'])
def pesquisar():
    nome_filme = request.form.get('nome_filme')
    nome = session_flask.get('nome')
    usuario_id = session_flask.get('usuario_id')
    try:
        resultados = api_service.filtrar_filmes(nome_filme)
        
        # Recupera as avaliações do filme pelo user_id
        avaliacoes = session.query(Ratings).filter_by(user_id=usuario_id).all()

        # Buscar as avaliações do banco de dados
        avaliacoes_usuario = [
            {
                'movie_api_id': avaliacao.movie_api_id,
                'rating': avaliacao.rating
            }
            for avaliacao in avaliacoes
        ]
        recomendacoes_ids = recomendador.recomendar_filmes_hibrido(usuario_id, avaliacoes_usuario)
        
        # Agora, obtemos os detalhes dos filmes recomendados usando o método da API
        filmes_recomendados = []
        for recomendacao in recomendacoes_ids:
            filme = recomendacao
            filmes_recomendados.append(filme)
            
        return render_template('filmes.html', nome=nome, id=usuario_id, resultados=resultados.get('results', []), filmes_recomendados=filmes_recomendados)
    except request.exceptions.HTTPError as e:
        return render_template('filmes.html', nome=nome, id=usuario_id, error=f'Erro na requisição: {e}')
    
@main.route('/filme/<int:id>', methods=['GET'])
def get_filme(id):
    filme = api_service.get_filme_by_id(id)
    return render_template('filme.html', filme=filme)

# Rota de avaliação do filme
@main.route('/filme/avaliar/<int:id>', methods=['POST'])
def avaliar_filme(id):
    if request.method == 'POST':
        # Recebe a avaliação do formulário
        rating_value = request.form.get('rating', type=float)
        usuario_id = session_flask.get('usuario_id')

        if not usuario_id:
            error = 'Usuário não autenticado'
            return redirect(url_for('main.index', error=error))

        if not (0.0 <= rating_value <= 5.0):
            error = 'A avaliação deve estar entre 0.0 e 5.0'
            return redirect(url_for('main.filmes', id=id, error=error))

        # Verifica se o filme já existe no dataset
        caminho_movies_path = recomendador.caminho_movies()
        try:
            df_movies = pd.read_csv(caminho_movies_path)
        except Exception as e:
            error = f"Erro ao carregar o dataset de filmes: {e}"
            return redirect(url_for('main.index', error=error))
        
        filme_existente = df_movies[df_movies['movieId'] == id]

        if filme_existente.empty:
            # Se o filme não estiver no dataset, buscamos na API
            try:
                api_service_en = ApiFilmesService(api_key, 'en-US')
                filme = api_service_en.get_filme_by_id(id)
                if filme:
                    # Certifique-se de que o filme é um dicionário JSON válido
                    if isinstance(filme, dict) and 'title' in filme and 'genres' in filme:
                        # Extraindo os nomes dos gêneros e juntando-os em uma string
                        genres = [genre['name'] for genre in filme['genres']]
                        genres_str = '|'.join(genres)  # Salvando os gêneros como uma string

                        # Criando o novo filme a ser adicionado ao dataset
                        novo_filme = pd.DataFrame([{
                            'movieId': id,
                            'title': filme['title'],
                            'genres': genres_str  # Salvando os gêneros como uma string
                        }])

                        # Usando pd.concat() para adicionar o novo filme ao dataset
                        df_movies = pd.concat([df_movies, novo_filme], ignore_index=True)

                        # Gravando de volta no CSV
                        df_movies.to_csv(caminho_movies_path, index=False)
                    else:
                        error = 'Estrutura de dados do filme não é válida ou incompleta.'
                        return redirect(url_for('main.index', error=error))
                else:
                    error = 'Filme não encontrado na API externa.'
                    return redirect(url_for('main.index', error=error))
            except Exception as e:
                error = f"Erro ao buscar o filme na API: {e}"
                return redirect(url_for('main.index', error=error))

        # Agora registramos a avaliação do filme
        avaliacao_existente = session.query(Ratings).filter_by(user_id=usuario_id, movie_api_id=id).first()
        if avaliacao_existente:
            # Atualiza a avaliação existente
            avaliacao_existente.rating = rating_value
            session.commit()
            success = 'Avaliação atualizada com sucesso!'
        else:
            # Registra uma nova avaliação
            nova_avaliacao = Ratings(user_id=usuario_id, movie_api_id=id, rating=rating_value)
            session.add(nova_avaliacao)
            session.commit()
            success = 'Avaliação registrada com sucesso!'

        return redirect(url_for('main.filmes', id=id, success=success))


    
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
    
    # Recupera as avaliações do filme pelo user_id
    avaliacoes = session.query(Ratings).filter_by(user_id=usuario_id).all()

    # Buscar as avaliações do banco de dados
    avaliacoes_usuario = [
        {
            'movie_api_id': avaliacao.movie_api_id,
            'rating': avaliacao.rating
        }
        for avaliacao in avaliacoes
    ]

    # Passar as avaliações para o método da service
    recomendacoes = recomendador.recomendar_filmes_hibrido(usuario_id, avaliacoes_usuario)

    return jsonify(recomendacoes)

@main.route('/alterar_senha/<int:usuario_id>', methods=['POST'])
def alterar_senha(usuario_id):
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_nova_senha = request.form.get('confirm_nova_senha')
        
        # Recupera o usuário do banco de dados
        user = session.query(User).filter_by(user_id=usuario_id).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verifica se a senha atual está correta
        if not bcrypt.checkpw(senha_atual.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Senha atual inválida'}), 401
        
        # Verifica se a nova senha e a confirmação são iguais
        if nova_senha != confirmar_nova_senha:
            return jsonify({'error': 'Nova senha e confirmação devem ser iguais'}), 400
        
        # Hasheia a nova senha e atualiza no banco
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = nova_senha_hash
        session.commit()
        
        success = 'Senha alterada com sucesso'
        return redirect(url_for('main.filmes', id=usuario_id, success=success))

 
