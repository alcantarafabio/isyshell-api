from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db, AuditLogModel
from app.schemas import AuditLogOut
from app.auth import verify_token

router = APIRouter(prefix="/api/v1/logs", tags=["Auditoria"])


@router.get("/", response_model=List[AuditLogOut], summary="Listar logs de auditoria")
def list_logs(
    script_name: Optional[str] = Query(None, description="Filtrar por nome do script"),
    status: Optional[str] = Query(None, description="Filtrar por status: success | error"),
    limit: int = Query(50, ge=1, le=500, description="Máximo de registros retornados"),
    offset: int = Query(0, ge=0, description="Paginação — offset inicial"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = db.query(AuditLogModel)

    if script_name:
        q = q.filter(AuditLogModel.script_name == script_name)
    if status:
        q = q.filter(AuditLogModel.status == status)

    items = q.order_by(AuditLogModel.executed_at.desc()).offset(offset).limit(limit).all()

    return items


@router.get("/summary", summary="Resumo estatístico dos logs")
def logs_summary(
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    from sqlalchemy import func

    rows = (
        db.query(
            AuditLogModel.script_name,
            AuditLogModel.status,
            func.count(AuditLogModel.id).label("count"),
        )
        .group_by(AuditLogModel.script_name, AuditLogModel.status)
        .all()
    )

    summary: dict = {}
    for script_name, status, count in rows:
        if script_name not in summary:
            summary[script_name] = {"success": 0, "error": 0, "total": 0}
        summary[script_name][status] = count
        summary[script_name]["total"] += count

    return {"summary": summary, "scripts_count": len(summary)}
