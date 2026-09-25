import sqlite3
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from database import get_db

router = APIRouter()

#Schema de validação de dados recebidos no corpo da requisição
class FuncionarioSchema(BaseModel):
    nome: str
    matricula: str
    setor: str

#Cadastrar um funcionario 
@router.post("/funcionarios", status_code=status.HTTP_201_CREATED)
def cadastrar_funcionario(funcionario: FuncionarioSchema, db: sqlite3.Connection = Depends(get_db)):    
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO funcionarios (nome, matricula, setor)
                VALUES (?, ?, ?)
            """, (funcionario.nome, funcionario.matricula, funcionario.setor))
            db.commit()
            return {"mensagem": "Funcionário cadastrado com sucesso!"}
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A matricula '{funcionario.matricula}' já está cadastrada para outro funcionário"
            )
        
 #Listar todos os funcionários
@router.get("/funcionarios")
def listar_funcionarios(db: sqlite3.Connection = Depends(get_db)):    
        cursor = db.cursor()
        cursor.execute("SELECT * FROM funcionarios")
        funcionarios = cursor.fetchall()
        return [dict(row) for row in funcionarios]

#Consulta o funcionário por id
@router.get("/funcionario/{funcionario_id}")
def obter_funcionario(funcionario_id: int, db: sqlite3.Connection = Depends(get_db)):    
        cursor = db.cursor()
        cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (funcionario_id,))
        funcionario = cursor.fetchone()

        if not funcionario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funcionário com ID {funcionario_id} não encontrado."
            )
        return dict(funcionario)


#Atualiza o funcionario
@router.put("/funcionario/{funcionario_id}")
def atualizar_funcionario(funcionario_id: int, funcionario: FuncionarioSchema, db: sqlite3.Connection = Depends(get_db)):    
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE funcionarios
                SET nome = ?, matricula = ?, setor = ?
                WHERE id = ?
            """, (funcionario.nome, funcionario.matricula, funcionario.setor, funcionario_id))
            db.commit()

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Funcionário com ID {funcionario_id} não encontrado."
                )
            return {"mensagem": "Dados do funcionário atualizados com sucesso!"}
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A matrícula'{funcionario.matricula}' já pertence a outro funcionário."
            )

#Deletar funcionário
@router.delete("/funcionarios/{funcionario_id}")
def deletar_funcionario(funcionario_id: int, db: sqlite3.Connection = Depends(get_db)):    
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM funcionarios WHERE id = ?", (funcionario_id,))
            db.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Funcionário com ID {funcionario_id} não encontrado."
                )
            return {"mensagem": "Funcionário excluído com sucesso!"}
        except sqlite3.IntegrityError:
            #Caso existam frequências ou entregas vinculadas a este funcionário
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir este funcionário pois ele possui entregas associadas"
            )