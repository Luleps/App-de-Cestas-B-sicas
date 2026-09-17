from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter()

@router.get("/entregas/pendentes")
def listar_todas_pendentes():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                f.nome, f.matricula, c.mes, c.ano, e.id as entrega_id, e.status
            FROM entregas e
            JOIN funcionarios f ON f.id = e.funcionario_id
            JOIN competencias c ON c.id = e.competencia_id
            WHERE e.status = 'pendente'
            ORDER BY c.ano ASC, c.mes ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

@router.patch("/entregas/{entrega_id}/confirmar")
def confirmar_entrega(entrega_id: int):
    with get_db() as conn:
        cursor = conn.cursor
        cursor.execute("""
            UPDATE entregas
            SET status = 'entregue', data_entrega = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pendente'
        """, (entrega_id))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=400, detail="Entrega não encontrada ou já realizada")
        return {"mensagem": "Cesta entregue com sucesso!"}