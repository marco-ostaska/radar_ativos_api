import sqlite3
import os

def init_transacoes():
    # Conecta ao banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'radar_ativos.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Lê o arquivo SQL
        sql_path = os.path.join(os.path.dirname(__file__), 'init_transacoes.sql')
        with open(sql_path, 'r') as file:
            sql_commands = file.read()

        # Executa os comandos SQL
        cursor.executescript(sql_commands)
        conn.commit()
        print("Tabela de transações criada com sucesso!")

    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    init_transacoes() 