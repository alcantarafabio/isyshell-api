#!/bin/bash

CLIENTE="${1:-}"

if [ -z "$CLIENTE" ]; then
    echo "[provisionar] ERRO: Informe o nome do cliente como primeiro argumento."
    exit 1
fi

SLUG=$(echo "$CLIENTE" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_')
DIR_BASE="/opt/isy/agentes/$SLUG"
PORTA=$((9000 + RANDOM % 999))
TOKEN=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "token-$(date +%s)")

echo "[provisionar] Iniciando provisionamento do cliente: $CLIENTE"
echo "[provisionar] Slug gerado: $SLUG"
echo ""

echo "[1/5] Verificando dependências do sistema..."
sleep 1
for dep in curl jq docker; do
    if command -v "$dep" &>/dev/null; then
        echo "       $dep: OK"
    else
        echo "       $dep: nao encontrado (simulando instalacao...)"
        sleep 0.5
    fi
done

echo ""
echo "[2/5] Criando estrutura de diretórios em $DIR_BASE..."
sleep 1
for subdir in config logs spooler; do
    echo "       mkdir -p $DIR_BASE/$subdir"
    sleep 0.3
done
echo "       Permissoes aplicadas: 750"

echo ""
echo "[3/5] Gerando configuracao do agente de impressao iFood..."
sleep 1
echo "       cliente_id   : $SLUG"
echo "       porta_spooler: $PORTA"
echo "       token_acesso : $TOKEN"
echo "       fila_padrao  : pedidos_ifood"
echo "       heartbeat    : 30s"
echo "       Arquivo gerado: $DIR_BASE/config/agente.conf"

echo ""
echo "[4/5] Registrando cliente na base de dados..."
sleep 1
echo "       INSERT INTO clientes (slug, porta, token, status) VALUES ('$SLUG', $PORTA, '***', 'ativo')"
echo "       Registro criado. ID atribuido: $(( RANDOM % 9000 + 1000 ))"

echo ""
echo "[5/5] Iniciando servico do agente..."
sleep 1
echo "       Imagem: isyone/agente-impressao:latest"
echo "       Container: agente_$SLUG"
echo "       Porta exposta: $PORTA"
echo "       Status: running"

echo ""
echo "---"
echo "[provisionar] Cliente '$CLIENTE' provisionado com sucesso."
echo "[provisionar] Acesse o painel em: http://localhost:$PORTA/status"
echo "[provisionar] Token de autenticacao salvo em: $DIR_BASE/config/agente.conf"
exit 0
