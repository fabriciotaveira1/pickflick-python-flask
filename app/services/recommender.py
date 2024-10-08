import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from surprise import Dataset, Reader, SVD


class RecomendadorDeFilmesService:
    def __init__(self):
        # Importando dataset de avaliações
        self.df_avaliacoes = pd.read_csv('movie_datasets/ratings.csv')
        self.df_avaliacoes.drop(columns=['timestamp'], inplace=True)

        # Importando dataset de filmes
        self.df_filmes = pd.read_csv('movie_datasets/movies.csv')

        # Vetorização dos gêneros dos filmes
        vetorizador = CountVectorizer()
        self.matriz_generos = vetorizador.fit_transform(self.df_filmes['genres'])

        # Similaridade de cosseno entre os gêneros
        self.similaridade_generos = cosine_similarity(self.matriz_generos, self.matriz_generos)

        # Preparando os dados para o Surprise
        reader = Reader(rating_scale=(1, 5))

        # Renomeando colunas para o formato esperado pelo Surprise
        self.df_avaliacoes = self.df_avaliacoes.rename(columns={'user_id': 'userId', 'movie_id': 'movieId'})

        # Carregando os dados para o Surprise
        dados_surprise = Dataset.load_from_df(self.df_avaliacoes[['userId', 'movieId', 'rating']], reader)

        # Treinando o modelo de filtragem colaborativa (SVD)
        trainset = dados_surprise.build_full_trainset()
        self.modelo_svd = SVD()
        self.modelo_svd.fit(trainset)

    def prever_avaliacao(self, usuario_id, filme_id):
        # Prever a avaliação com o modelo SVD
        predicao = self.modelo_svd.predict(usuario_id, filme_id).est
        return predicao

    def recomendar_filmes_hibrido(self, usuario_id, top_n=3):
        recomendacoes = {}

        # Percorrer todos os filmes para gerar uma pontuação ponderada por similaridade de gênero
        for idx, row in self.df_filmes.iterrows():
            filme_id = row['movieId']

            # Prever a avaliação para o filme
            avaliacao_prevista = self.prever_avaliacao(usuario_id, filme_id)

            # Calcular a média de similaridade com outros filmes já assistidos pelo usuário
            similaridades = []
            filmes_assistidos = self.df_avaliacoes[self.df_avaliacoes['userId'] == usuario_id]['movieId']
            for filme_assistido_id in filmes_assistidos:
                idx_assistido = self.df_filmes[self.df_filmes['movieId'] == filme_assistido_id].index[0]
                idx_atual = self.df_filmes[self.df_filmes['movieId'] == filme_id].index[0]
                similaridades.append(self.similaridade_generos[idx_atual, idx_assistido])

            # Calcular a média de similaridades
            if similaridades:
                similaridade_media = sum(similaridades) / len(similaridades)
            else:
                similaridade_media = 0

            # Calcular a pontuação final (ponderando a previsão pelo gênero)
            score_final = avaliacao_prevista * similaridade_media
            recomendacoes[filme_id] = score_final

        # Ordenar as recomendações pelos scores e retornar os top N
        filmes_recomendados = sorted(recomendacoes.items(), key=lambda x: x[1], reverse=True)[:top_n]

        return [(self.df_filmes[self.df_filmes['movieId'] == filme_id]['title'].values[0], score)
                for filme_id, score in filmes_recomendados]
