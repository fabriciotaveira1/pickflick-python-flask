import requests

class ApiFilmesService:
    def __init__(self, api_key):
        self.base_url = 'https://api.themoviedb.org/3/movie/'
        self.api_key = api_key
        self.language = 'pt-BR'
        self.filter_url = 'https://api.themoviedb.org/3/search/movie?api_key='  # URL para busca de filmes

    def _build_url(self, endpoint, additional_params=''):
        """Constrói a URL completa para a requisição."""
        return f'{self.base_url}{endpoint}?api_key={self.api_key}&language={self.language}{additional_params}'

    def listar_filmes_populares(self, page=1):
        """Lista os filmes populares."""
        url = self._build_url('popular', f'&page={page}')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def listar_melhores_avaliados(self, page=1):
        """Lista os filmes mais bem avaliados."""
        url = self._build_url('top_rated', f'&page={page}')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def listar_filmes_nos_cinemas(self):
        """Lista os filmes que estão em cartaz nos cinemas."""
        url = self._build_url('now_playing', '&page=1&region=BR')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def filtrar_filmes(self, nome_filme):
        """Filtra filmes pelo nome fornecido."""
        search_url = f'{self.filter_url}{self.api_key}&language={self.language}&query={nome_filme}'
        response = requests.get(search_url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_filme_by_id(self, id_filme):
        """Obtém informações sobre um filme específico pelo ID."""
        url = self._build_url(f'{id_filme}')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_credits_filme(self, id_filme):
        """Obtém os créditos de um filme específico pelo ID."""
        url = self._build_url(f'{id_filme}/credits')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_providers(self, id_filme):
        """Obtém os provedores de streaming para um filme específico pelo ID."""
        url = self._build_url(f'{id_filme}/watch/providers')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_genres(self):
        """Obtém a lista de gêneros de filmes."""
        genres_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={self.api_key}&language={self.language}'
        response = requests.get(genres_url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def discover_movies(self, page=1):
        """Descobre filmes com base em parâmetros específicos."""
        discover_url = f'https://api.themoviedb.org/3/discover/movie?api_key={self.api_key}&include_adult=false&sort_by=vote_count.desc&page={page}'
        response = requests.get(discover_url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
