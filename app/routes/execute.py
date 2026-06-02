import os
import subprocess
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, ScriptModel, AuditLogModel
from app.schemas import ExecuteRequest, ExecuteResponse
from app.auth import verify_token

router = APIRouter(prefix="/api/v1/execute", tags=["Execução"])

SCRIPTS_DIR = os.getenv("SCRIPTS_DIR", "/opt/isyone/scripts")
TIMEOUT_SECONDS = int(os.getenv("SCRIPT_TIMEOUT", "120"))


def _build_safe_path(filename: str) -> str:
    # prevents path traversal
    safe_path = os.path.realpath(os.path.join(SCRIPTS_DIR, filename))
    allowed_prefix = os.path.realpath(SCRIPTS_DIR)
    if not safe_path.startswith(allowed_prefix + os.sep) and safe_path != allowed_prefix:
        raise HTTPException(
            status_code=400,
            detail="Tentativa de acesso fora do diretório de scripts bloqueada.",
        )
    return safe_path


def _write_audit_log(
    db: Session,
    script: ScriptModel,
    params: list,
    result: subprocess.CompletedProcess | None = None,
    error_msg: str | None = None,
) -> AuditLogModel:
    status = "success" if (result and result.returncode == 0) else "error"
    log = AuditLogModel(
        script_name=script.name,
        filename=script.filename,
        params_used=" ".join(params) if params else None,
        status=status,
        stdout=result.stdout if result else None,
        stderr=result.stderr if result else error_msg,
        exit_code=result.returncode if result else -1,
        executed_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.post(
    "/{script_name}",
    response_model=ExecuteResponse,
    summary="Executar script pelo nome",
)
def execute_script(
    script_name: str,
    payload: ExecuteRequest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    script = db.query(ScriptModel).filter_by(name=script_name).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script '{script_name}' não cadastrado.")
    if not script.active:
        raise HTTPException(status_code=403, detail=f"Script '{script_name}' está desativado.")

    script_path = _build_safe_path(script.filename)
    if not os.path.isfile(script_path):
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo '{script.filename}' não encontrado em {SCRIPTS_DIR}.",
        )

    if not os.access(script_path, os.X_OK):
        os.chmod(script_path, 0o755)

    cmd = [script_path] + (payload.params or [])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            # shell=False prevents command injection
        )
    except subprocess.TimeoutExpired:
        log = _write_audit_log(db, script, payload.params or [], error_msg="Timeout excedido")
        raise HTTPException(
            status_code=504,
            detail=f"Script excedeu o limite de {TIMEOUT_SECONDS}s. Log ID: {log.id}",
        )
    except Exception as exc:
        log = _write_audit_log(db, script, payload.params or [], error_msg=str(exc))
        raise HTTPException(status_code=500, detail=f"Erro interno: {exc}. Log ID: {log.id}")

    log = _write_audit_log(db, script, payload.params or [], result=result)

    return ExecuteResponse(
        status="success" if result.returncode == 0 else "error",
        script=script.name,
        params_used=payload.params or [],
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        executed_at=log.executed_at,
        log_id=log.id,
    )
