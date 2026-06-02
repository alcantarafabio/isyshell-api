#!/bin/bash
# cleanup_logs.sh — Remove logs de cupons com mais de 30 dias
# Uso: ./cleanup_logs.sh

LOG_DIR="/var/log/isyone/cupons"
DAYS_OLD=30

echo "[cleanup_logs] Iniciando limpeza de logs com mais de ${DAYS_OLD} dias..."

if [ ! -d "$LOG_DIR" ]; then
    echo "[cleanup_logs] Diretório $LOG_DIR não encontrado — criando estrutura de exemplo."
    mkdir -p "$LOG_DIR"
    echo "[cleanup_logs] Nenhum log para remover."
    exit 0
fi

REMOVED=$(find "$LOG_DIR" -type f -name "*.log" -mtime +${DAYS_OLD} | wc -l)
find "$LOG_DIR" -type f -name "*.log" -mtime +${DAYS_OLD} -delete

echo "[cleanup_logs] $REMOVED arquivo(s) removido(s)."
echo "[cleanup_logs] Limpeza concluída com sucesso."
exit 0
