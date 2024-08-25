# PICKFLICK

## Tema

<p>Sistema de Recomendação de Filmes/Músicas Personalizado: Um sistema que usa algoritmos de aprendizado de máquina para recomendar filmes ou músicas com base nas preferências do usuário. Pode envolver o uso de técnicas de filtragem colaborativa ou baseada em conteúdo.</p>

## Variáveis

### Estrutura do Banco de Dados
- Tabela users: Armazena as informações dos usuários.

<p>user_id (INT, PRIMARY KEY, AUTO_INCREMENT): Identificador único do usuário.</p>
<p>username (VARCHAR(50)): Nome do usuário.</p>
<p>email (VARCHAR(100)): Email do usuário.</p>
<p>password (VARCHAR(100)): Senha criptografada do usuário.</p>
<p>created_at (TIMESTAMP): Data de criação do usuário.</p>

- Tabela movies: Armazena as informações dos filmes.

<p>movie_id (INT, PRIMARY KEY, AUTO_INCREMENT): Identificador único do filme.</p>
<p>title (VARCHAR(255)): Título do filme.</p>
<p>genre (VARCHAR(100)): Gênero do filme.</p>
<p>release_year (YEAR): Ano de lançamento.</p>
<p>duration (INT): Duração do filme em minutos.</p>
<p>director (VARCHAR(100)): Nome do diretor.</p>
<p>synopsis (TEXT): Sinopse do filme.</p>

- Tabela ratings: Armazena as avaliações dos filmes pelos usuários.

<p>rating_id (INT, PRIMARY KEY, AUTO_INCREMENT): Identificador único da avaliação.</p>
<p>user_id (INT, FOREIGN KEY): Referência ao usuário que fez a avaliação.</p>
<p>movie_id (INT, FOREIGN KEY): Referência ao filme avaliado.</p>
<p>rating (DECIMAL(2,1)): Avaliação dada pelo usuário (por exemplo, de 0.0 a 5.0).</p>
<p>rated_at (TIMESTAMP): Data e hora da avaliação.</p>

- Tabela user_preferences: Armazena as preferências dos usuários em termos de gêneros de filmes.

<p>preference_id (INT, PRIMARY KEY, AUTO_INCREMENT): Identificador único da preferência.</p>
<p>user_id (INT, FOREIGN KEY): Referência ao usuário.</p>
<p>genre (VARCHAR(100)): Gênero preferido do usuário.</p>
<p>preference_level (INT): Nível de preferência para o gênero (por exemplo, de 1 a 10).</p>


#### Dependências Utilizadas
- Flask, pandas, jinja2, sqlAlchemy, scikit-learn"# pickflick-python-flask" 
