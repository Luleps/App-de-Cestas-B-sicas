from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
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
    """
    if faltas_injustificadas > 0:
        return False, f"Inelegível ({faltas_injustificadas} falta(s) injustificada(s))"
    if dias_trabalhados < 15:
        return False, f"Inelegível ({dias_trabalhados} dias trabalhados - mín. 15)"
    return True, "Elegível"

#1. Obter status das entregas de uma competência
@router.get("/entregas/status")
def listar_status_entregas(competencia_id: int = Query, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    #Busca frequências registradas
    query = """
        SELECT            
            func.id AS funcionario_id,
            func.nome,
            func.matricula,
            func.setor
            c.id AS competencia_id,
            c.mes,
            c.ano,
            COUNT(f.id) AS dias_trabalhados,
            e.id AS entrega_id,
            COALESCE(e.entregue, 0) AS entregue,
            e.data_entrega
        FROM funcionarios func
        CROSS JOIN competencias c
        LEFT JOIN frequencia f
            ON f.funcionario_id = func.id
            AND strftime('%m', f.data) = printf('%02d', c.mes)
            AND strftime('%Y', f.data) = CAST(c.ano AS TEXT)
        LEFT JOIN entregas e
            ON e.funcionario_id = func.id
            AND e.competencia_id = c.id
        WHERE c.id = ? -- Passe o id da competencia desejada via parametro
        GROUP BY func.id, c.id;
        """
    
    cursor.execute(query, (competencia_id))
    registros = cursor.fetchall()

    resultado = []
    for r in registros:
        # Se sua regra não calcula faltas injustificadas na query, passe 0
        faltas_inj = 0 
        elegivel, motivo = verificar_elegibilidade(r["dias_trabalhados"], faltas_inj)

        resultado.append({
            "entrega_id": r["entrega_id"],
            "funcionario_id": r["funcionario_id"],
            "nome": r["nome"],
            "matricula": r["matricula"],
            "setor": r["setor"],
            "competencia": f"{r['mes']:02d}/{r['ano']}",
            "dias_trabalhados": r["dias_trabalhados"],
            "faltas_injustificadas": faltas_inj,
            "elegivel": elegivel,
            "motivo_elegibilidade": motivo,
            "entregue": bool(r["entregue"]),
            "data_entrega": r["data_entrega"]
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