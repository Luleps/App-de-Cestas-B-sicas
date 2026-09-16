import sqlite3

conn = sqlite3.connect("cestas_basicas.br")
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
CREATE TABLE IF NOT EXISTS competencia (
id INTEGER PRIMARY KEY AOTUINCREMENT,
mes INTEGER NOT NULL,
ano INTEGER NOT NULL
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
FOREIGN KEY(competencia_id) REFERNCES competencias(id)
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
FOREIGN KEY (competencia_id) REFERENCES competencia(id),
) 
""")

# Trigger de elegibilidade
cursor.execute("""
CREATE TRIGGER IF NOT EXISTS validar_elegibilidade
AFTER INSERT ON frequencia
FOR EACH ROW
BEGIN
    INSERT INTO entregas (funcionario_ id, competencia_id, status)
    VALUES (
        NEW.funcionario_id,
        NEW.competencia_id,
        CASE 
            WHEN NEW.dias_trabalhados >= 15 AND NEW.faltas_injustificadas = 0
                THEN 'pendente'
            ELSE 'atrasada'
        END
    );
END;
""")
conn.commit()
conn.close()