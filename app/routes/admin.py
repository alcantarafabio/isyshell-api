import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, ConfigModel
from app.schemas import TokenUpdate
from app.auth import verify_token

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/token/info", summary="Verificar status do token atual")
def token_info(
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    config = db.query(ConfigModel).filter_by(key="api_token").first()
    if not config:
        raise HTTPException(status_code=503, detail="Configuração de token ausente.")
    return {
        "token_length": len(config.value),
        "last_updated": config.updated_at,
        "hint": f"{config.value[:4]}...{config.value[-4:]}",
    }


@router.put("/token", summary="Rotacionar token de autenticação")
def update_token(
    payload: TokenUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    config = db.query(ConfigModel).filter_by(key="api_token").first()
    if not config:
        config = ConfigModel(key="api_token", value=payload.new_token)
        db.add(config)
    else:
        config.value = payload.new_token
        config.updated_at = datetime.utcnow()

    db.commit()
    return {
        "status": "success",
        "message": "Token atualizado com sucesso. Use o novo token nas próximas requisições.",
        "hint": f"{payload.new_token[:4]}...{payload.new_token[-4:]}",
    }


@router.post("/token/generate", summary="Gerar e aplicar novo token aleatório")
def generate_token(
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    new_token = str(uuid.uuid4())
    config = db.query(ConfigModel).filter_by(key="api_token").first()
    if config:
        config.value = new_token
        config.updated_at = datetime.utcnow()
    else:
        db.add(ConfigModel(key="api_token", value=new_token))
    db.commit()

    return {
        "status": "success",
        "new_token": new_token,
        "message": "Guarde este token em local seguro — não será exibido novamente.",
    }
