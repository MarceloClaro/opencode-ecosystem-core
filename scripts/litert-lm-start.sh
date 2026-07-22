#!/bin/bash
# ============================================================================
# LiteRT-LM Auto-Start Script
# ============================================================================
# Inicia o servidor litert-lm serve em background se não estiver rodando.
# Uso:
#   ./scripts/litert-lm-start.sh          # Inicia (se necessário) e sai
#   ./scripts/litert-lm-start.sh --status  # Mostra status
#   ./scripts/litert-lm-start.sh --stop    # Para o servidor
#   ./scripts/litert-lm-start.sh --log     # Mostra log
#
# Instalação como serviço (systemd --user):
#   mkdir -p ~/.config/systemd/user/
#   cat > ~/.config/systemd/user/litert-lm.service << 'SERVICE'
#   [Unit]
#   Description=LiteRT-LM Server (Gemma 4 on-device)
#   After=network-online.target
#
#   [Service]
#   Type=simple
#   ExecStart=%h/opencode-ecosystem-core/scripts/litert-lm-start.sh
#   Restart=on-failure
#   RestartSec=10
#
#   [Install]
#   WantedBy=default.target
#   SERVICE
#   systemctl --user daemon-reload
#   systemctl --user enable --now litert-lm.service
# ============================================================================

PORT=9379
LOG_DIR="$HOME/.litert-lm"
LOG_FILE="$LOG_DIR/server.log"
PID_FILE="$LOG_DIR/server.pid"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$LOG_DIR"

# ── Detectar processo existente ────────────────────────────────────────────

check_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            # Verifica se é realmente um processo litert-lm
            if ps -p "$pid" -o cmd= 2>/dev/null | grep -q "litert-lm.*serve"; then
                return 0
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Procura por processo órfão
    local pid=$(pgrep -f "litert-lm.*serve.*--port $PORT" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        echo "$pid" > "$PID_FILE"
        return 0
    fi
    
    return 1
}

check_http() {
    curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/v1/models" 2>/dev/null | grep -q 200
}

# ── Comandos ───────────────────────────────────────────────────────────────

case "${1:-}" in
    --status)
        if check_pid; then
            echo "LiteRT-LM: RUNNING (PID $(cat $PID_FILE))"
            if check_http; then
                echo "  HTTP: OK (port $PORT)"
                echo "  Models:"
                curl -s "http://localhost:$PORT/v1/models" | python3 -m json.tool 2>/dev/null | grep '"id"' | sed 's/.*"id": "//;s/".*//' | sed 's/^/    - /'
            else
                echo "  HTTP: NOT RESPONDING"
            fi
        else
            echo "LiteRT-LM: STOPPED"
        fi
        exit 0
        ;;
    
    --stop)
        if check_pid; then
            local pid=$(cat "$PID_FILE")
            echo "Parando LiteRT-LM (PID $pid)..."
            kill "$pid" 2>/dev/null
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            rm -f "$PID_FILE"
            echo "OK."
        else
            echo "LiteRT-LM não está rodando."
        fi
        exit 0
        ;;
    
    --log)
        if [ -f "$LOG_FILE" ]; then
            tail -50 "$LOG_FILE"
        else
            echo "Log file not found: $LOG_FILE"
        fi
        exit 0
        ;;
    
    --restart)
        "$0" --stop
        sleep 1
        "$0"
        exit $?
        ;;
esac

# ── Auto-start ─────────────────────────────────────────────────────────────

if check_pid; then
    echo "LiteRT-LM já está rodando (PID $(cat $PID_FILE))."
    exit 0
fi

if check_http; then
    # Servidor respondendo mas sem PID registrado
    echo "LiteRT-LM está respondendo na porta $PORT (órfão)."
    local pid=$(pgrep -f "litert-lm.*serve.*--port $PORT" 2>/dev/null | head -1)
    echo "$pid" > "$PID_FILE"
    exit 0
fi

echo "Iniciando LiteRT-LM na porta $PORT..."
nohup litert-lm serve --port "$PORT" --cors-origin "*" > "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

echo "Aguardando servidor ficar pronto..."
for i in $(seq 1 60); do
    if check_http; then
        echo "LiteRT-LM pronto! (PID $PID, ${i}s)"
        echo "Log: $LOG_FILE"
        exit 0
    fi
    sleep 2
done

echo "Timeout: LiteRT-LM não iniciou em 120s."
echo "Verifique o log: $LOG_FILE"
rm -f "$PID_FILE"
exit 1
