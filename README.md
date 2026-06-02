# 🐚 IsyShell API

> **Orquestrador Automático de Infraestrutura — ISY.ONE**  
> Hackathon FMU Tech 2026 · `github.com/alcantarafabio/isyshell-api`

Converta rotinas críticas de terminal em um **microsserviço seguro, auditável e conteinerizado**.

---

## 🏗️ Arquitetura dos 5 Pilares

| # | Pilar | Implementação |
|---|-------|--------------|
| 1 | **API RESTful + subprocess** | FastAPI + `subprocess.run()` sem `shell=True` |
| 2 | **Segurança X-Isy-Token** | Middleware de validação contra banco SQLite |
| 3 | **Cadastro de Scripts** | CRUD completo + rotação dinâmica de token |
| 4 | **Logs de Auditoria** | SQLite com horário, script, params e status |
| 5 | **Dockerfile** | `python:3.11-slim`, usuário não-root, volumes |

---

## 🚀 Subindo com Docker Compose

```bash
# Clone o repositório
git clone https://github.com/alcantarafabio/isyshell-api.git
cd isyshell-api

# (Opcional) Defina seu token inicial
export ISY_TOKEN="meu-token-super-secreto-2026"

# Build e start
docker compose up -d --build

# Acompanhe os logs
docker compose logs -f
```

A API estará disponível em: **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

---

## 🔐 Autenticação

Todas as rotas (exceto `/`) exigem o header:

```
X-Isy-Token: <seu-token>
```

O token inicial é gerado automaticamente no primeiro boot e exibido nos logs do container:

```bash
docker compose logs isyshell-api | grep "Token inicial"
```

---

## 📋 Endpoints Principais

### Scripts

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/scripts/` | Lista scripts cadastrados |
| `POST` | `/api/v1/scripts/` | Cadastra novo script |
| `PATCH` | `/api/v1/scripts/{id}` | Atualiza descrição/status |
| `DELETE` | `/api/v1/scripts/{id}` | Remove script |

### Execução

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/execute/{script_name}` | Executa script com parâmetros |

**Exemplo de payload:**
```json
{
  "params": ["meu_cliente", "8155"]
}
```

### Auditoria

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/logs/` | Lista logs com filtros e paginação |
| `GET` | `/api/v1/logs/summary` | Resumo estatístico por script |

### Administração

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/admin/token/info` | Metadados do token atual |
| `PUT` | `/api/v1/admin/token` | Atualiza token manualmente |
| `POST` | `/api/v1/admin/token/generate` | Gera novo token UUID automático |

---

## 🛡️ Segurança

- `subprocess.run()` **sem** `shell=True` — elimina injeção via metacaracteres
- Validação de parâmetros: bloqueia `;`, `|`, `&`, `` ` ``, `$`, `<`, `>` e outros
- Proteção contra **path traversal** com `os.path.realpath()`
- Container rodando com **usuário não-root** (`uid=1001`)
- Scripts montados como volume **read-only** (`:ro`)
- Token armazenado em banco — **rotação sem restart**

---

## 📁 Estrutura do Projeto

```
isyshell-api/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── database.py      # SQLAlchemy + modelos SQLite
│   ├── schemas.py       # Pydantic schemas + validações
│   ├── auth.py          # Validação X-Isy-Token
│   └── routes/
│       ├── scripts.py   # CRUD de scripts
│       ├── execute.py   # Execução subprocess
│       ├── logs.py      # Auditoria
│       └── admin.py     # Rotação de token
├── scripts/             # Shell scripts (montado via volume)
│   ├── cleanup_logs.sh
│   └── check_status.sh
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧪 Teste Rápido com curl

```bash
# Descubra o token inicial
TOKEN=$(docker compose exec isyshell-api \
  python -c "from app.database import SessionLocal, ConfigModel; \
  db=SessionLocal(); print(db.query(ConfigModel).filter_by(key='api_token').first().value)")

# Liste os scripts cadastrados
curl -H "X-Isy-Token: $TOKEN" http://localhost:8000/api/v1/scripts/

# Execute o cleanup_logs
curl -X POST \
  -H "X-Isy-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"params": []}' \
  http://localhost:8000/api/v1/execute/cleanup_logs

# Veja os logs de auditoria
curl -H "X-Isy-Token: $TOKEN" http://localhost:8000/api/v1/logs/
```

---

## 🔮 Diferenciais e Próximos Passos

- [ ] Webhook de alerta (Discord/Telegram) em falhas críticas
- [ ] Fila assíncrona com Celery + Redis para scripts demorados
- [ ] Interface web React para gestão dos scripts
- [ ] Autenticação JWT com escopos por script
- [ ] Rate limiting por token

---

© 2026 ISY.ONE — Hackathon FMU Tech
