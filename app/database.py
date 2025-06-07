from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./radar_ativos.db"

# Criar engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base para os modelos
Base = declarative_base()

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para adicionar campo ativo nas tabelas
def adicionar_campo_ativo():
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    cursor = conn.cursor()
    
    try:
        # Adiciona campo ativo na tabela transacoes_acoes
        cursor.execute("""
            ALTER TABLE transacoes_acoes 
            ADD COLUMN ativo BOOLEAN DEFAULT 1
        """)
        
        # Adiciona campo ativo na tabela transacoes_fii
        cursor.execute("""
            ALTER TABLE transacoes_fii 
            ADD COLUMN ativo BOOLEAN DEFAULT 1
        """)
        
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Campos já existem")
        else:
            raise e
    finally:
        conn.close()

# Executa a função para adicionar os campos
adicionar_campo_ativo() 