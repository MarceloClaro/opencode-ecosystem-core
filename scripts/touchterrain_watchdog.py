#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TouchTerrain Watchdog — auto-recuperação de hangs (SPEC-935-R145)
==================================================================
Mitigação operacional para o defeito observado em 16/07/2026: threads do
gunicorn (worker gthread) bloqueadas indefinidamente em chamadas de rede
ao Earth Engine sem timeout próprio, esgotando o pool de threads e
deixando o endpoint /main sem resposta (hang), sem que o `--timeout 600`
do gunicorn (que opera no nível de worker, não de thread individual)
detecte o problema.

Este script:
  1. Testa periodicamente um endpoint leve do TouchTerrain (`/main`) com
     um timeout curto.
  2. Se o endpoint não responder dentro do timeout (ou responder com
     erro), reinicia o serviço systemd via `systemctl restart`.
  3. É idempotente: cada execução faz no máximo UMA tentativa de
     verificação e UMA tentativa de restart — a repetição periódica é
     responsabilidade do timer systemd externo (não deste script).

Uso:
  python3 scripts/touchterrain_watchdog.py
  python3 scripts/touchterrain_watchdog.py --url http://localhost:8081/main \\
      --service geomaker-touchterrain --timeout 10

Sem dependências externas — apenas biblioteca padrão do Python.
"""
import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "http://localhost:8081/main"
DEFAULT_SERVICE = "geomaker-touchterrain"
DEFAULT_TIMEOUT = 10.0


def check_health(url: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """Retorna True se `url` responder com status HTTP < 500 dentro do
    timeout; False em qualquer falha (timeout, conexão recusada, 5xx)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status < 500
    except urllib.error.HTTPError as e:
        # HTTPError também carrega o status — 4xx ainda conta como "vivo"
        return e.code < 500
    except Exception:
        return False


def restart_service(service_name: str) -> bool:
    """Reinicia um serviço systemd via `systemctl restart`. Retorna True
    se o comando terminou com código de saída 0."""
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", service_name],
            timeout=60,
        )
        return result.returncode == 0
    except Exception:
        return False


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] touchterrain_watchdog: {msg}", file=sys.stderr, flush=True)


def run_once(url: str = DEFAULT_URL, service: str = DEFAULT_SERVICE,
             timeout: float = DEFAULT_TIMEOUT) -> bool:
    """Executa um ciclo de verificação. Retorna True se estava saudável
    (nenhuma ação tomada) ou se a remediação teve sucesso; False se a
    remediação foi tentada e falhou."""
    saudavel = check_health(url, timeout=timeout)
    if saudavel:
        log(f"OK — {url} respondeu dentro de {timeout}s")
        return True

    log(f"FALHA — {url} não respondeu em {timeout}s; reiniciando {service}...")
    ok = restart_service(service)
    if ok:
        log(f"Serviço {service} reiniciado com sucesso.")
    else:
        log(f"ERRO ao reiniciar {service}. Intervenção manual pode ser necessária.")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--service", default=DEFAULT_SERVICE)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    ok = run_once(url=args.url, service=args.service, timeout=args.timeout)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
