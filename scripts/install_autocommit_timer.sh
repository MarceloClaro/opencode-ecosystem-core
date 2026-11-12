#!/usr/bin/env bash
# Instala timer systemd --user para checkpoint automático a cada 2 minutos.
set -euo pipefail

REPO_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE="$UNIT_DIR/opencode-autocommit.service"
TIMER="$UNIT_DIR/opencode-autocommit.timer"

mkdir -p "$UNIT_DIR"

cat >"$SERVICE" <<EOF
[Unit]
Description=OpenCode Ecosystem Core - checkpoint e push automaticos
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$REPO_ROOT
ExecStart=$REPO_ROOT/scripts/autocommit_push.sh
Nice=10
IOSchedulingClass=idle
EOF

cat >"$TIMER" <<'EOF'
[Unit]
Description=Executa o checkpoint automatico do Core a cada 2 minutos

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
Persistent=true
AccuracySec=30s

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now opencode-autocommit.timer
systemctl --user --no-pager list-timers opencode-autocommit.timer
