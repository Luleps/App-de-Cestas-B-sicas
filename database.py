import sqlite3

DB_PATH = 'cestas_basicas_db'

def init_db():
    """Cria as tabelas necessárias caso elas não existam."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Garante suporte a chaves estrangeiras durante a criação
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        senha TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        matricula TEXT UNIQUE NOT NULL,
        setor TEXT,
        usuario_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuario (id)
    );

    CREATE TABLE IF NOT EXISTS competencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL,
        mes INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS frequencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        funcionario_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        FOREIGN KEY (funcionario_id) REFERENCES funcionarios (id)
    );
    CREATE TABLE IF NOT EXISTS entregas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        funcionario_id INTEGER NOT NULL,
        competencia_id INTEGER NOT NULL,
        entregue INTEGER DEFAULT 0,
        data_entrega TEXT,
        FOREIGN KEY (funcionario_id) REFERENCES funcionarios (id),
        FOREIGN KEY (competencia_id) REFERENCES competencias (id)
    );
    """)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()
