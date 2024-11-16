import os
import pickle
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from decimal import Decimal

class RecomendadorDeFilmesService:
    def __init__(self):
        # Caminhos absolutos dos datasets
        caminho_ratings = os.path.join('app', 'services', 'movie_datasets', 'ratings.csv')
        caminho_movies = os.path.join('app', 'services', 'movie_datasets', 'movies.csv')

        # Importando dataset de avaliações e filmes
        self.df_avaliacoes = pd.read_csv(caminho_ratings)
        self.df_filmes = pd.read_csv(caminho_movies)

        # Processamento dos dados
        self.df_avaliacoes.drop(columns=['timestamp'], inplace=True)
        
        # Variável para armazenar o ID mapeado do usuário atual
        self.usuario_atual_id_mapeado = None

        # Vetorização dos gêneros dos filmes
        vetorizador = CountVectorizer()
        self.matriz_generos = vetorizador.fit_transform(self.df_filmes['genres'])
        self.similaridade_generos = cosine_similarity(self.matriz_generos, self.matriz_generos)

        # Mapeamento de movieId para índice para eficiência
        self.movie_index_map = {movie_id: idx for idx, movie_id in enumerate(self.df_filmes['movieId'])}

        # Inicializa e treina o modelo na inicialização
        self.modelo_knn = self.verificar_ou_treinar_modelo()
        
    def caminho_movies(self):
        return os.path.join('app', 'services','movie_datasets','movies.csv')

    def verificar_ou_treinar_modelo(self):
        modelo_path = os.path.join('app', 'services', 'modelo_treinado', 'modelo_knn.pkl')

        # Verifica se o modelo já foi treinado
        if os.path.exists(modelo_path):
            with open(modelo_path, 'rb') as file:
                print("Modelo carregado a partir do arquivo.")
                return pickle.load(file)
        else:
            print("Modelo não encontrado. Treinando novo modelo...")

            # Treina o modelo KNN
            X = self.df_avaliacoes[['userId', 'movieId']]
            y = self.df_avaliacoes['rating']
            
            # Criação e treinamento do modelo KNN
            modelo_knn = KNeighborsRegressor(n_neighbors=5, algorithm='auto', n_jobs=-1)  # Usa todos os núcleos de CPU disponíveis
            modelo_knn.fit(X, y)

            # Salva o modelo treinado
            os.makedirs(os.path.dirname(modelo_path), exist_ok=True)
            with open(modelo_path, 'wb') as file:
                pickle.dump(modelo_knn, file)
            
            print("Modelo treinado e salvo com sucesso.")
            return modelo_knn
    
    def mapear_usuario_id(self, usuario_real_id, inicio=612):
        """Mapeia o ID do usuário atual para um ID do dataset, começando no valor de `inicio`"""
        max_id_dataset = self.df_avaliacoes['userId'].max()
        self.usuario_atual_id_mapeado = max_id_dataset + 1 if max_id_dataset >= inicio else inicio
        return self.usuario_atual_id_mapeado


    def calcular_media_avaliacao_usuario(self, avaliacoes_usuario):
        if not avaliacoes_usuario:
            # Se não houver avaliações do usuário, retorna a média geral
            return self.df_avaliacoes['rating'].mean()

        # Calcula a média das notas do usuário
        media_avaliacao = sum(avaliacao['rating'] for avaliacao in avaliacoes_usuario) / len(avaliacoes_usuario)
        return media_avaliacao
    def recomendar_filmes_hibrido(self, usuario_id, avaliacoes_usuario, top_n=8):
        media_avaliacao_usuario = self.calcular_media_avaliacao_usuario(avaliacoes_usuario)

        filmes_assistidos = [avaliacao['movie_api_id'] for avaliacao in avaliacoes_usuario]

        recomendacoes = {}

        for idx, row in self.df_filmes.iterrows():
            filme_id = row['movieId']

            # Similaridade média com filmes assistidos
            if filmes_assistidos:
                idx_atual = self.movie_index_map.get(filme_id, None)
                if idx_atual is not None:
                    indices_assistidos = [self.movie_index_map[movie_id] for movie_id in filmes_assistidos if movie_id in self.movie_index_map]
                    similaridades = self.similaridade_generos[idx_atual, indices_assistidos]
                    similaridade_media = similaridades.mean()
                else:
                    similaridade_media = 0
            else:
                similaridade_media = 0

            # Score final usando a média de avaliação
            score_final = Decimal(media_avaliacao_usuario) * Decimal(similaridade_media)
            recomendacoes[filme_id] = score_final

        # Se o usuário não tiver avaliações, retornar os 8 melhores filmes
        if not filmes_assistidos:
            # Calcula a média de avaliações de cada filme
            filmes_com_media = self.df_avaliacoes.groupby('movieId')['rating'].mean().reset_index()
            filmes_com_media = filmes_com_media.merge(self.df_filmes, on='movieId')
            melhores_filmes = filmes_com_media.nlargest(8, 'rating')[['movieId', 'title']]

            return melhores_filmes.to_dict(orient='records')

        filmes_recomendados = sorted(recomendacoes.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{'id': filme_id, 'titulo': self.df_filmes.loc[self.df_filmes['movieId'] == filme_id, 'title'].values[0]} 
                for filme_id, _ in filmes_recomendados]

