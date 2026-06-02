from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, ScriptModel
from app.schemas import ScriptCreate, ScriptOut, ScriptUpdate
from app.auth import verify_token

router = APIRouter(prefix="/api/v1/scripts", tags=["Scripts"])


@router.get("/", response_model=List[ScriptOut], summary="Listar todos os scripts")
def list_scripts(
    active_only: bool = False,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = db.query(ScriptModel)
    if active_only:
        q = q.filter(ScriptModel.active == True)
    return q.order_by(ScriptModel.name).all()


@router.get("/{script_id}", response_model=ScriptOut, summary="Buscar script por ID")
def get_script(
    script_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    script = db.query(ScriptModel).filter(ScriptModel.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script ID {script_id} não encontrado.")
    return script


@router.post("/", response_model=ScriptOut, status_code=201, summary="Cadastrar novo script")
def create_script(
    payload: ScriptCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    if db.query(ScriptModel).filter_by(name=payload.name).first():
        raise HTTPException(status_code=409, detail=f"Script com name='{payload.name}' já existe.")

    script = ScriptModel(**payload.model_dump())
    db.add(script)
    db.commit()
    db.refresh(script)
    return script


@router.patch("/{script_id}", response_model=ScriptOut, summary="Atualizar script")
def update_script(
    script_id: int,
    payload: ScriptUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    script = db.query(ScriptModel).filter(ScriptModel.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script ID {script_id} não encontrado.")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(script, field, value)

    db.commit()
    db.refresh(script)
    return script


@router.delete("/{script_id}", status_code=204, summary="Remover script")
def delete_script(
    script_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    script = db.query(ScriptModel).filter(ScriptModel.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script ID {script_id} não encontrado.")
    db.delete(script)
    db.commit()
