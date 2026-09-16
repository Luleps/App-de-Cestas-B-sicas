from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db_connection

router = APIRouter()

class Funcionario(BaseModel):
    nome: str
    matricula: str
    setor: str

@router.post("/funcionarios")
def cadastrar_funcionario(func: Funcionario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO funcionarios (nome, matricula, setor)
         VALUES (?, ?, ?) 
    """, (func.nome, func.matricula, func.setor))
    conn.commit()
    conn.close()
    return {"mensagem": "Funcionario cadastrado com sucesso!"}

@router.get("/funcionarios")
def listar_funcionarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM funcionarios")
    funcionarios  = cursor.fetchall()
    conn.close()
    return [{"id": row["id"], "nome": row["nome"], "matricula": row["matricula"], "setor": row["setor"]} for row in funcionarios]