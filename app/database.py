import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.getenv("DB_PATH", "/data/isyshell.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScriptModel(Base):
    __tablename__ = "scripts"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False, index=True)
    filename    = Column(String(255), nullable=False)           # e.g. cleanup_logs.sh
    description = Column(String(500), nullable=True)
    parameters  = Column(String(500), nullable=True)            # descrição dos params
    active      = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id          = Column(Integer, primary_key=True, index=True)
    script_name = Column(String(100), nullable=False, index=True)
    filename    = Column(String(255), nullable=False)
    params_used = Column(String(500), nullable=True)
    status      = Column(String(20), nullable=False)            # success | error
    stdout      = Column(Text, nullable=True)
    stderr      = Column(Text, nullable=True)
    exit_code   = Column(Integer, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)


class ConfigModel(Base):
    __tablename__ = "config"

    key        = Column(String(100), primary_key=True)
    value      = Column(String(500), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_default_data():
    """Garante token padrão e scripts de exemplo no banco."""
    import uuid
    db = SessionLocal()
    try:
        # Token padrão se não existir
        token_row = db.query(ConfigModel).filter_by(key="api_token").first()
        if not token_row:
            default_token = os.getenv("ISY_TOKEN", str(uuid.uuid4()))
            db.add(ConfigModel(key="api_token", value=default_token))
            db.commit()
            print(f"[IsyShell] Token inicial gerado: {default_token}")

        # Scripts de exemplo
        scripts_dir = os.getenv("SCRIPTS_DIR", "/opt/isyone/scripts")
        examples = [
            {
                "name": "cleanup_logs",
                "filename": "cleanup_logs.sh",
                "description": "Remove logs de cupons com mais de 30 dias",
                "parameters": "nenhum",
            },
            {
                "name": "check_status",
                "filename": "check_status.sh",
                "description": "Verifica status dos containers Docker do cliente",
                "parameters": "client_name (string)",
            },
            {
                "name": "provisionar",
                "filename": "provisionar.sh",
                "description": "Provisiona novo ambiente para cliente",
                "parameters": "client_name (string), domain (string), port (int)",
            },
        ]
        for s in examples:
            if not db.query(ScriptModel).filter_by(name=s["name"]).first():
                db.add(ScriptModel(**s))
        db.commit()
    finally:
        db.close()
