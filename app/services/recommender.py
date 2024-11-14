import os
import pickle
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

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

        # Vetorização dos gêneros dos filmes
        vetorizador = CountVectorizer()
        self.matriz_generos = vetorizador.fit_transform(self.df_filmes['genres'])
        self.similaridade_generos = cosine_similarity(self.matriz_generos, self.matriz_generos)

        # Mapeamento de movieId para índice para eficiência
        self.movie_index_map = {movie_id: idx for idx, movie_id in enumerate(self.df_filmes['movieId'])}

        # Inicializa e treina o modelo na inicialização
        self.modelo_knn = self.verificar_ou_treinar_modelo()

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

    def calcular_media_avaliacao_usuario(self, usuario_id):
        avaliacoes_usuario = self.df_avaliacoes[self.df_avaliacoes['userId'] == usuario_id]['rating']
        return avaliacoes_usuario.mean() if not avaliacoes_usuario.empty else self.df_avaliacoes['rating'].mean()

    def recomendar_filmes_hibrido(self, usuario_id, top_n=3):
        media_avaliacao_usuario = self.calcular_media_avaliacao_usuario(usuario_id)
        filmes_assistidos = self.df_avaliacoes[self.df_avaliacoes['userId'] == usuario_id]['movieId']
        
        recomendacoes = {}

        for idx, row in self.df_filmes.iterrows():
            filme_id = row['movieId']

            # Similaridade média com filmes assistidos
            if not filmes_assistidos.empty:
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
            score_final = media_avaliacao_usuario * similaridade_media
            recomendacoes[filme_id] = score_final

        filmes_recomendados = sorted(recomendacoes.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{'id': filme_id, 'titulo': self.df_filmes.loc[self.df_filmes['movieId'] == filme_id, 'title'].values[0]} 
                for filme_id, _ in filmes_recomendados]
