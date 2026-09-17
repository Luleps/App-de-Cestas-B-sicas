import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from database import get_db

router = APIRouter()

class CompetenciaSchema(BaseModel):
    mes: int = Field(ge=1, le=12, description="Mês entre 1 e 12")
    ano: int = Field(ge= 2019, description="Ano válido a partir de 2019")

#CREATE
@router.post("/competencias", status_code=status.HTTP_201_CREATED)
def criar_competencia(comp: CompetenciaSchema):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO competencias (mes, ano)
            VALUES (?, ?)
            """, (comp.mes, comp.ano))
            conn.commit()
            return {"mensagem":f"Competência {comp.mes:02d}/{comp.ano} criada com sucesso!"}
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A competência {comp.mes:02d}/{comp.ano} já for cadastrada."
            )

#READ ALL
@router.get("/competencias")
def listar_competencias():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM competencias ORDER BY ano DESC, mes DESC")
        return [dict(row) for row in cursor.fetchall()]