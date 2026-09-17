import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import get_db

router = APIRouter()

#Schema de validação de dados recebidos no corpo da requisição
class Funcionario(BaseModel):
    nome: str
    matricula: str
    setor: str

#Rota para cadastrar um funcionario com tratamento de erros
@router.post("/funcionarios", status_code=status.HTTP_201_CREATED)
def cadastrar_funcionario(func: Funcionario):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO funcionarios (nome, matricula, setor)
                VALEU (?, ?, ?)
            """, (func.nome, func.matricula, func.setor))
            conn.commit()
            return {"mensagem": "Funcionário cadastrado com sucesso!"}
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A matricula '{func.matricula}' já está cadastrada para outro funcionário"
            )
        
 #Rota para listar todos os funcionários
@router.get("/funcionarios")
def listar_funcionarios():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funcionarios")
        funcionarios = cursor.fetchall()
        return [dict(row) for row in funcionarios]
