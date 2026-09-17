import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import get_db

router = APIRouter()

#Schema de validação de dados recebidos no corpo da requisição
class FuncionarioShema(BaseModel):
    nome: str
    matricula: str
    setor: str

#Rota para cadastrar um funcionario com tratamento de erros
@router.post("/funcionarios", status_code=status.HTTP_201_CREATED)
def cadastrar_funcionario(func: FuncionarioShema):
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

#Consulta o funcionário
@router.get("/funcionario/{funcionario_id}")
def obter_funcionario(funcionario_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (funcionario_id,))
        funcionario = cursor.fetchone()

        if not funcionario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funcionário com ID não encontrado."
            )
        return dict(funcionario)


#Atualiza o funcionario
@router.put("/funcionario/{funcionario_id}")
def atualizar_funcionario(funcionario_id: int, func: FuncionarioShema):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPTADE funcionarios
                SET nome = ?, matricula = ?, setor = ?
                WHERE id = ?
            """, (func.nome, func.matricula, func.setor, funcionario_id))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Funcionário com ID não encontrado."
                )
            return {"mensagem": "Dados do funcionário atualizados com sucesso!"}
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Amatrícula '{func.matricula}' já pertence a outro funcionário."
            )

#Deletar funcionário
@router.delete("/funcionarios/{funcionario_id}")
def deletar_funcionario(funcionario_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM funcionarios WHERE id = ?", (funcionario_id))
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Funcionário com ID não encontrado."
                )
            return {"mensagem": "Funcionário excluído com sucesso!"}
        except sqlite3.IntegrityError:
            #Caso existam frequências ou entregas vinculadas a este funcionário
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir este funcionário pois ele possui entregas associadas"
            )