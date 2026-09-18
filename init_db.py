import sqlite3

conn = sqlite3.connect("cestas_basicas.db")
cursor = conn.cursor()

# Tabela de funcionários
cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT NOT NULL,
matricula TEXT UNIQUE NOT NULL,
setor TEXT)
""")

# Tabela de Competência
cursor.execute(""" 
CREATE TABLE IF NOT EXISTS competencias (
id INTEGER PRIMARY KEY AUTOINCREMENT,
mes INTEGER NOT NULL,
ano INTEGER NOT NULL,
UNIQUE(mes, ano)
)
""")

# Tabela de Frequência
cursor.execute("""
CREATE TABLE IF NOT EXISTS frequencia (
id INTEGER PRIMARY KEY AUTOINCREMENT,
funcionario_id INTEGER NOT NULL,
competencia_id INTEGER NOT NULL,
dias_trabalhados INTEGER NOT NULL,
faltas_justificadas INTEGER DEFAULT 0,
faltas_injustificadas INTEGER DEFAULT 0,
FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id),
FOREIGN KEY(competencia_id) REFERENCES competencia(id)
)
""")

# Tabela de Entregas
cursor.execute("""
CREATE TABLE IF NOT EXISTS entregas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
funcionario_id INTEGER NOT NULL,
competencia_id INTEGER NOT NULL,
status TEXT CHECK (status IN ('pendente', 'entregue', 'atrasada')) NOT NULL,
FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
FOREIGN KEY (competencia_id) REFERENCES competencia(id)) 
""")

# Trigger de elegibilidade
cursor.execute("""
CREATE TRIGGER IF NOT EXISTS validar_elegibilidade
AFTER INSERT ON frequencia
FOR EACH ROW
BEGIN
    INSERT INTO entregas (funcionario_id, competencia_id, status)
    VALUES (
        NEW.funcionario_id,
        NEW.competencia_id,
        CASE 
            WHEN NEW.dias_trabalhados >= 15 AND NEW.faltas_injustificadas = 0
                THEN 'pendente'
            ELSE 'inelegivel'
        END
    );
END;
""")
conn.commit()
conn.close()