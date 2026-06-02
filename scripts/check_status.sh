#!/bin/bash
# check_status.sh — Verifica status dos containers Docker de um cliente
# Uso: ./check_status.sh <client_name>

CLIENT_NAME="${1:-}"

if [ -z "$CLIENT_NAME" ]; then
    echo "[check_status] ERRO: Informe o nome do cliente como primeiro argumento."
    exit 1
fi

echo "[check_status] Verificando containers do cliente: $CLIENT_NAME"

if command -v docker &>/dev/null; then
    CONTAINERS=$(docker ps -a --filter "name=${CLIENT_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null)
    if [ -z "$CONTAINERS" ]; then
        echo "[check_status] Nenhum container encontrado para: $CLIENT_NAME"
    else
        echo "$CONTAINERS"
    fi
else
    echo "[check_status] Docker não disponível neste ambiente."
fi

echo "[check_status] Verificação concluída."
exit 0
