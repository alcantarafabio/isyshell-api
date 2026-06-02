from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
import re


class ScriptCreate(BaseModel):
    name: str
    filename: str
    description: Optional[str] = None
    parameters: Optional[str] = None
    active: bool = True

    @field_validator("filename")
    @classmethod
    def filename_must_be_sh(cls, v: str) -> str:
        if not v.endswith(".sh"):
            raise ValueError("filename deve terminar com .sh")
        # evita path traversal
        if "/" in v or "\\" in v or ".." in v:
            raise ValueError("filename não pode conter barras ou '..'")
        return v

    @field_validator("name")
    @classmethod
    def name_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
            raise ValueError("name deve ser alfanumérico (a-z, 0-9, _ ou -)")
        return v


class ScriptUpdate(BaseModel):
    description: Optional[str] = None
    parameters: Optional[str] = None
    active: Optional[bool] = None


class ScriptOut(BaseModel):
    id: int
    name: str
    filename: str
    description: Optional[str]
    parameters: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExecuteRequest(BaseModel):
    params: Optional[List[str]] = []

    @field_validator("params")
    @classmethod
    def sanitize_params(cls, params: list) -> list:
        FORBIDDEN = re.compile(r'[;&|`$<>()\\\n\r\x00]')
        sanitized = []
        for p in params:
            p = str(p)
            if FORBIDDEN.search(p):
                raise ValueError(
                    f"Parâmetro inválido detectado: '{p}' — "
                    "metacaracteres shell não são permitidos."
                )
            if len(p) > 256:
                raise ValueError("Parâmetro excede 256 caracteres.")
            sanitized.append(p)
        return sanitized


class ExecuteResponse(BaseModel):
    status: str
    script: str
    params_used: List[str]
    exit_code: int
    stdout: str
    stderr: str
    executed_at: datetime
    log_id: int


class AuditLogOut(BaseModel):
    id: int
    script_name: str
    filename: str
    params_used: Optional[str]
    status: str
    stdout: Optional[str]
    stderr: Optional[str]
    exit_code: Optional[int]
    executed_at: datetime

    class Config:
        from_attributes = True


class TokenUpdate(BaseModel):
    new_token: str

    @field_validator("new_token")
    @classmethod
    def token_min_length(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("Token deve ter no mínimo 16 caracteres.")
        return v
