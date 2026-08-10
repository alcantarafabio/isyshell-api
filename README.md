# IsyShell API

Projeto desenvolvido para o Hackathon FMU 2026.1 com ISY.ONE.

A ideia surgiu de um problema real: a equipe de suporte da ISY.ONE precisa rodar scripts de terminal toda hora pra fazer manutenção nos clientes - limpeza de logs, verificação de status, reinicialização de serviços. Isso toma tempo, gera erro humano e não fica registrado em lugar nenhum.

A IsyShell API resolve isso expondo esses scripts via HTTP. Em vez de alguém abrir SSH, digitar o comando e torcer pra não errar, qualquer ferramenta (Zapier, n8n, um painel interno) pode chamar a API e disparar o script automaticamente. 

## Como funciona

A API foi feita com FastAPI e executa os scripts usando `subprocess.run()` sem `shell=True`. Essa escolha foi intencional: com `shell=True`, alguém poderia passar um parâmetro como `; rm -rf /` e o sistema executaria sem reclamar. Isso se chama Command Injection, e aqui está bloqueado. Também tem proteção contra Path Traversal - o caminho real do script é validado com `os.path.realpath()` pra garantir que nada fora da pasta permitida seja acessado.

Para chamar qualquer endpoint, é preciso passar o header `X-Isy-Token`. O token fica salvo num banco SQLite e pode ser rotacionado sem reiniciar nada. Os scripts são cadastrados via CRUD - adiciona, atualiza, remove - e cada execução fica registrada com horário, parâmetros e resultado.

Tudo roda em Docker com a imagem `python:3.11-slim`. O processo sobe como usuário não-root e os scripts são montados como volume read-only, então o container não tem como modificar os arquivos da máquina host.

## Como rodar

```bash
git clone https://github.com/alcantarafabio/isyshell-api.git
cd isyshell-api
```

Antes de subir, edite o valor de `ISY_TOKEN` no `docker-compose.yml` com um token de sua escolha. Depois:

```bash
docker compose up --build
```

A API fica em http://localhost:8000. O Swagger com todos os endpoints está em http://localhost:8000/docs.

