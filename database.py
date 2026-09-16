import sqlite3

# Obijeto de conexao com o banco de dados

def get_db_connection():
    conn = sqlite3.connect("cestas_basicas.db")
    conn.row_factory = sqlite3.Row
    return conn