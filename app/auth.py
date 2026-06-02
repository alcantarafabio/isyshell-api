from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db, ConfigModel


def verify_token(
    x_isy_token: str = Header(..., description="Token de autenticação da API"),
    db: Session = Depends(get_db),
) -> str:
    config = db.query(ConfigModel).filter_by(key="api_token").first()
    if not config:
        raise HTTPException(status_code=503, detail="Configuração de token não encontrada.")

    if x_isy_token != config.value:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou ausente. Acesso negado.",
            headers={"WWW-Authenticate": "X-Isy-Token"},
        )

    return x_isy_token
