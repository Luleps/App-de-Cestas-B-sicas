from fastapi import APIRouter
from database import get_db_connection

router = APIRouter()

@router.get("/elegiveis/{competencia_id}")
def listar_elegiveis(competencia_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.nome, e.status
        FROM funcionarios f
        JOIN entregas e ON f.id = e.funcionario_id
        WHERE e.competencia_id = ? AND e.status = 'pendente'
    """, (competencia_id,))
    resultados = cursor.fetchall()
    conn.close()
    return [{"nome": row["nome"], "status": row["status"]} for row in resultados]