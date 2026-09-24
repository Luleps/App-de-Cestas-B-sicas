from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
from database import get_db

router = APIRouter()

#Modelos Pydantic
class RegistrarEntregaSchema(BaseModel):
    funcionario_id: int
    competencia_id: int
    entregue: bool = True
    observacao: Optional[str] = None

#Regra de Negócio: Elegibilidade
def verificar_elegibilidade(dias_trabalhados: int, faltas_injustificadas: int) -> tuple[bool, str]:
    """
    Regra Padrão:
    - Minímo de 15 dias trabalhados na competência
    - No máximo 0 faltas injustificadas
    (Ajuste esses valores conforme regra da empresa)
    """
    if faltas_injustificadas > 0:
        return False, f"Inelegível ({faltas_injustificadas} falta(s) injustificada(s))"
    if dias_trabalhados < 15:
        return False, f"Inelegível ({dias_trabalhados} dias trabalhados - mín. 15)"
    return True, "Elegível"
#1. Obter status das entregas de uma competência
@router.get("/entregas/status")
def listar_status_entregas(competencia_id: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    #Busca frequências registradas
    query = """
        SELECT
            f.id as frequencia_id,
            func.id as funcionario_id,
            func.nome,
            func.matricula,
            func.setor,
            c.id as competencia_id,
            c.mes,
            c.ano,
            f.dias_trabalhados,
            f.faltas_justificadas,
            f.faltas_injustificadas,
            e.id as entrega_id,
            e.entregue,
            e.data_entrega,
            e.observacao
        FROM frequencia f
        JOIN funcionarios func ON f.funcionario_id = func.id
        JOIN competencias c ON f.competencia_id = c.id
        LEFT JOIN entregas e ON e.funcionario_id = func.id AND e.competencia_id = c.id
        """
    params = []
    if competencia_id:
        query += " WHERE f.competencia_id = ?"
        params.append(competencia_id)

    cursor.execute(query, params)
    registros = cursor.fetchall()

    resultado = []
    for r in registros:
        elegivel, motivo = verificar_elegibilidade(r["dias_trabalhados"], r["faltas_injustificadas"])
        resultado.append({
            "frequencia_id": r["frequencia_id"],
            "funcionario_id": r["funcionario_id"],
            "nome": r["nome"],
            "matricula": r["matricula"],
            "setor": r["setor"],
            "competencia": f"{r['mes']:02d}/{r['ano']}",
            "dias_trabalhados": r["dias trabalhados"],
            "faltas_injustificadas": r["faltas_injustificadas"],
            "elegivel": elegivel,
            "motivo_elegibilidade": motivo,
            "entregue": bool(r["Entregue"]) if r["entregue"] is not None else False,
            "data_entrega": r["data_entrega"],
            "observacao": r["observacao"]
        })
    return resultado

#2. Registrar ou atualizar entrega
@router.post("/entregas/registrar")
def registrar_entrega(dados: RegistrarEntregaSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    #Verifica se já existe registro de entrega
    cursor.execute(
        "SELECT id FROM entregas WHERE funcionario_id = ? AND competencia_id = ?",
        (dados.funcionario_id, dados.competencia_id)
    )
    existente = cursor.fetchone()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if existente:
        cursor.execute(
            """
            UPDATE entregas
            SET entregue = ?, data_entrega = ?, observacao = ?
            WHERE id = ?
            """,
            (1 if dados.entregue else 0, data_atual, dados.observacao, existente["id"])
        )
    else: 
        cursor.execute(
            """
            INSERT INTO entregas (funcionario_id, competencia_id, entregue, data_entrega, observacao)
            VALUES (?, ?, ?, ?, ?)
            """,
            (dados.funcionario_id, dados.competencia_id, 1 if dados.entregue else 0, data_atual, dados.observacao)
        )
    db.commit()
    return {"mensagem": "Status da entrega atualizado com sucesso!"}