import pandas as pd
from sklearn.neighbors import NearestNeighbors
import os

class RecomendadorDeFilmesService:
    
    @staticmethod
    def carregar_datasets():
        """Carrega os datasets de ratings e filmes a partir de arquivos CSV."""
        # Obtém o diretório atual do script
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Sobe um nível para a raiz do projeto

        # Define os caminhos para os datasets
        ratings_path = os.path.join(base_dir, 'movie_datasets', 'ratings.csv')
        movies_path = os.path.join(base_dir, 'movie_datasets', 'movies.csv')

        # Carrega os datasets
        ratings = pd.read_csv(ratings_path)
        movies = pd.read_csv(movies_path)
        return ratings, movies

    @staticmethod
    def preparar_dados(ratings):
        """Converte o dataset de ratings em uma matriz de avaliações de filmes."""
        matriz_avaliacoes = ratings.pivot_table(
            index='userId', 
            columns='movieId', 
            values='rating', 
            fill_value=0
        )
        return matriz_avaliacoes

    @staticmethod
    def combinar_avaliacoes(avaliacoes_reais, ratings):
        """Combina as avaliações reais dos usuários com as do dataset de treino."""
        df_avaliacoes_reais = pd.DataFrame({
            'userId': [avaliacao.user_id for avaliacao in avaliacoes_reais],
            'movieId': [avaliacao.movie_api_id for avaliacao in avaliacoes_reais],
            'rating': [avaliacao.rating for avaliacao in avaliacoes_reais]
        })

        combined_ratings = pd.concat([ratings, df_avaliacoes_reais], ignore_index=True)

        return combined_ratings

    @staticmethod
    def recomendar_filmes(usuario_id, avaliacoes_reais, ratings, n_recommendations=7):
        """Usa o KNN para recomendar filmes para o usuário com base em suas avaliações."""
        combined_ratings = RecomendadorDeFilmesService.combinar_avaliacoes(avaliacoes_reais, ratings)
        matriz_avaliacoes = RecomendadorDeFilmesService.preparar_dados(combined_ratings)

        if matriz_avaliacoes.empty or usuario_id not in matriz_avaliacoes.index:
            return []  # Retorna uma lista vazia se não houver dados ou o usuário não tiver avaliações

        n_neighbors = min(n_recommendations, matriz_avaliacoes.shape[0])
        n_neighbors = max(1, n_neighbors)

        knn = NearestNeighbors(metric='cosine', algorithm='brute')
        knn.fit(matriz_avaliacoes.values)

        user_index = matriz_avaliacoes.index.tolist().index(usuario_id)
        distancias, indices = knn.kneighbors([matriz_avaliacoes.iloc[user_index].values], n_neighbors=n_neighbors)

        recomendacoes_filmes_ids = matriz_avaliacoes.columns[indices.flatten()].tolist()

        # Filtrar os filmes que o usuário já avaliou
        avaliacoes_usuario = matriz_avaliacoes.iloc[user_index]
        recomendacoes_filmes_ids = [movie_id for movie_id in recomendacoes_filmes_ids if avaliacoes_usuario[movie_id] == 0]

        return recomendacoes_filmes_ids[:n_recommendations]


    @staticmethod
    def obter_informacoes_filmes(movie_ids, movies):
        """Retorna os detalhes dos filmes recomendados."""
        return movies[movies['movieId'].isin(movie_ids)][['movieId', 'title', 'genres']]
