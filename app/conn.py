from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from app.models import Ratings, User_preferences, User
import urllib.parse

# Configurações de conexão
user = 'root'
password = urllib.parse.quote_plus('senai@123')
host = 'localhost'
database = 'pickflick'

# String de conexão
connection_string = f'mysql+pymysql://{user}:{password}@{host}/{database}'

# Criação do engine
engine = create_engine(connection_string)

# Refletir as tabelas do banco de dados
metadata = MetaData()
metadata.reflect(bind=engine)

# Mapeamento automático das tabelas para classes
Base = automap_base(metadata=metadata)
Base.prepare()

# Criação da sessão
Session = sessionmaker(bind=engine)
session = Session()

# Acessar as classes mapeadas, por exemplo:

# User = Base.classes.user
User = Base.classes.users

# Ratings = Base.classes.ratings
Ratings = Base.classes.ratings

# User_preferences = Base.classes.user_preferences
User_preferences = Base.classes.user_preferences
