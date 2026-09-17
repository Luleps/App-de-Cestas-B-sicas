import sqlite3
from contextlib import contextmanager

DATABASE_NAME = "cestas_basicas.db"

# Obijeto de conexao com o banco de dados

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()