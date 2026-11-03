#!/usr/bin/env bash
# Atalho one-click para o instalador do Core. Padrão: somente diagnóstico.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 installer/oneclick/install.py "$@"
