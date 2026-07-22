import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient

# Carrega variáveis de ambiente com fallbacks seguros para desenvolvimento local
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:user_password@localhost:3306/restaurante")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_root:mongo_password@localhost:27017/")

# Configuração do MySQL com SQLAlchemy
# Usamos pool_pre_ping para reconectar automaticamente se a conexão expirar
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def obter_sessao_mysql():
    """Dependência para obter uma sessão de banco de dados MySQL."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuração do MongoDB (Motor/Pymongo)
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[os.getenv("MONGO_DB_NAME", "restaurante_logs")]

def obter_mongo_db():
    """Dependência para obter o banco de dados MongoDB."""
    return mongo_db
