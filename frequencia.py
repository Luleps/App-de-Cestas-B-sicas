import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from database import get_db

router = APIRouter()

# Schema para dados de frequência com validação Pydantic de não-negativos
class FrequenciaSchema(BaseModel):
    funcionario_id: int
    competencia_id: int
    dias_trabalhados: int = Field(ge=0, description="Dias trabalhados não podem ser negativos")
    faltas_justificadas: int = Field(default=0, ge=0)
    faltas_injustificadas: int = Field(default=0, ge=0)

class FrequenciaUpdateSchema(BaseModel):
    dias_trabalhados: int = Field(ge=0)
    faltas_justificadas: int = Field(default=0, ge=0)
    faltas_injustificadas: int = Field(default=0, ge=0)

#Create
@router.post("/frequencia", status_code=status.HTTP_201_CREATED)
def registrar_frequencia(freq: FrequenciaSchema):
    with get_db() as conn:
        cursor = conn.cursor()

        #1. Valida se o funcionário realmente existe
        cursor.execute("SELECT id FROM funcionario WHERE id = ?", (freq.funcionario_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funcionário com ID {freq.funcionario_id} não encontrado"
            )

        #2. Tenta registrar a frequência
        try:
            cursor.execute("""
                INSERT INTO frequencia (funcionario_id, competencia_id, dias_trabalhados, faltas_justificadas, faltas_injustificadas)
                VALUES (?, ?, ?, ?, ?)  
                """, (freq.funcionario_id, freq.competencia_id, freq.dias_trabalhados, freq.faltas_justificadas, freq.faltas_injustificadas))
            conn.commit()
            return {"mensagem": "Frequência registrada e elegibilidade processada com sucesso!"}
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A frequência deste funcionário já foi registrada para esta competência"
            )
#Consulta tudo e filtra por competencia
@router.get("/frequencia")
def listar_frequencias(competencia_id: int = None):
    with get_db() as conn:
        cursor = conn.cursor()
        if competencia_id:
            cursor.execute("SELECT * FROM frequencia WHERE competencia_id = ?", (competencia_id))
        else:
            cursor.execute("SELECT * FROM frequencia")
        return [dict(row) for row in cursor.fetchall()]

#UPDATE
@router.put("/frequencia/{frequencia_id}")
def atualizar_frequencia(frequencia_id: int, freq_data: FrequenciaUpdateSchema):
    with get_db as conn:
        cursor = conn.cursor()

        #1. Busca os dados atuais da frequência
        cursor.execute("SELECT funcionario_id, competencia_id FROM frequencia WHERE id = ?", (frequencia_id))
        frequencia_atual = cursor.fetchone()
        if not frequencia_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de frequencia ID {frequencia_id} não encontrado."
            )
        func_id = frequencia_atual["funcionario_id"]
        comp_id = frequencia_atual["competencia_id"]
        #2. Atualiza a tabela frequencia
        cursor.execute("""
            UPDATE frequencia
            SET dias_trabalhados = ?, faltas_justificadas = ?, faltas_injustificadas = ?
            WHERE id = ?
        """, (freq_data.dias_trabalhados, freq_data.faltas_justificadas, freq_data.faltas_injustificadas, frequencia_id))
        #3. Recalcula e atualiza a elegibilidade na tabela entregas(caso nao tenha sido entregue ainda)
        novo_status = 'pendente' if (freq_data.dias_trabalhados >= 15 and freq_data.faltas_injustificadas == 0) else "inelegivel"

        cursor.execute("""
            UPDATE entregas
            SET status = ?
            WHERE funcionario_id = ? AND competencia_id = ? AND status != 'entregue'
        """, (novo_status, func_id, comp_id))
        conn.commit()
        return {"mensagem": "Frequência e elegibilidade atualizadas com sucesso!"}

#DELETE
@router.delete("/frequencia/{frequencia_id}")
def deletar_frequencia(frequencia_id: int):
    with get_db as conn:
        cursor = conn.cursor()

        #Busca referências para remover também a entrega pendente correspondente
        cursor.execute("SELECT funcionario_id, competencia_id FROM frequencia_id WHERE id = ?", (frequencia_id))
        frequencia = cursor.fetchone()
        if not frequencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de frequência ID {frequencia_id} não encontrado."
            )
        #Remove a entrega gerada (somente se ainda estiver como pendente/inelegivel)
        cursor.execute("""
            DELETE FROM entregas
            WHERE funcionario_id = ? AND competencia_id = ? AND status != 'entregue'
        """, (frequencia["funcionario_id,"], frequencia["competencia_id"]))
        #Remove a frequencia
        cursor.execute("DELETE FROM frequencia WHERE id = ?", (frequencia_id))
        conn.commit()
        return {"mensagem": "Registro de frequência e pendência de entrega associada foram removidos com sucesso!"}
    