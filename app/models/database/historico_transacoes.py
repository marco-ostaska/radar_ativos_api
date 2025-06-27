import sqlite3

def criar_tabela_historico():
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade REAL NOT NULL,
            valor_total REAL NOT NULL,
            carteira_id INTEGER NOT NULL,
            proporcao_antes INTEGER,
            proporcao_depois INTEGER,
            FOREIGN KEY (carteira_id) REFERENCES carteiras (id)
        )
    """)
    
    conn.commit()
    conn.close() 