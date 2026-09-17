import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class Frequencia(BaseModel):
    funcionario_id: int
    competencia_id: int
    dias_trabalhados: int
    faltas_justificadas: int = 0
    faltas_injustificadas: int = 0

@router.post("/frequencia", status_code=status.HTTP_201_CREATED)
def registrar_frequencia(freq: Frequencia):
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
