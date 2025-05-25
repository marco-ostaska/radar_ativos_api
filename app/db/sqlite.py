import sqlite3
import os

def get_db():
    """
    Retorna a conexão com o banco de dados SQLite, usando absolute path.
    """
    # Diretório absoluto deste arquivo (db/sqlite.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho absoluto para o radar_ativos.db na pasta sqlite/
    db_path = os.path.join(base_dir, '..', '..', 'sqlite', 'radar_ativos.db')
    db_path = os.path.abspath(db_path)  # Garante que seja absoluto e normalizado

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
