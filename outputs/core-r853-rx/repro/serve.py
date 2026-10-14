"""Servidor dual-stack (IPv4 + IPv6) da reprodução (SPEC-935-R878 / R882).

Por que existe: o uvicorn (>=0.30) liga **apenas uma família** por processo —
`--host 127.0.0.1` atende só IPv4 e `--host ::` atende só IPv6 (ele força
`IPV6_V6ONLY=1`). Este launcher abre **um único socket** AF_INET6 em `[::]`
com `IPV6_V6ONLY=0`, que aceita IPv6 nativo **e** IPv4 mapeado (127.0.0.1 e
LAN), e o entrega pronto ao uvicorn via `Server.run(sockets=[...])`.

Uso local (dual-stack):
    RX_ENGINE=open_base RX_MEDSAM_CKPT=/caminho/medsam_vit_b.pth \
        python serve.py                 # a partir de repro/  (default porta 8799)
    RX_PORT=9000 python serve.py        # outra porta

Uso em nuvem / container (SPEC-935-R882): provedores publicam a app em
`0.0.0.0:$PORT` — defina `RX_HOST=0.0.0.0` e o provedor injeta `PORT`
(Render/Railway/Fly/Cloud Run). Sem `RX_HOST`, o default segue dual-stack `::`.

Segurança: com `[::]`/`0.0.0.0` o serviço fica exposto na rede; as rotas admin
da reprodução usam credenciais de **demonstração** — não use dados reais.
"""

from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
from typing import Mapping

import uvicorn

PORT = int(os.environ.get("RX_PORT", "8799"))
BACKEND = Path(__file__).resolve().parent / "backend"
LOGLVL = os.environ.get("RX_LOGLEVEL", "warning")


def _resolve_bind(env: Mapping[str, str] | None = None) -> tuple[str, int]:
    """Resolve (host, porta) do bind.

    Default local: host `::` (dual-stack) na porta `RX_PORT` ou 8799. Em nuvem,
    `PORT` (padrão do provedor) tem precedência sobre `RX_PORT`, e `RX_HOST`
    (ex.: `0.0.0.0`) define a interface.
    """
    env = os.environ if env is None else env
    port = int(env.get("PORT") or env.get("RX_PORT") or PORT)
    host = env.get("RX_HOST") or "::"
    return host, port


def _dualstack_socket(port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    except OSError:
        pass
    sock.bind(("::", port))
    sock.listen(2048)
    return sock


def main() -> None:
    # uvicorn>=0.30 não aceita mais app_dir: expõe o backend no sys.path.
    if str(BACKEND) not in sys.path:
        sys.path.insert(0, str(BACKEND))
    host, port = _resolve_bind()
    if host == "::":
        # Local: socket pré-ligado dual-stack (IPv4 + IPv6 num processo).
        sock = _dualstack_socket(port)
        config = uvicorn.Config(
            "app:app", host=host, port=port,
            log_level=LOGLVL, access_log=False,
        )
        server = uvicorn.Server(config)
        print(f"[serve] dual-stack em [::]:{port} (IPv6 + IPv4 mapeado)  backend={BACKEND}", flush=True)
        server.run(sockets=[sock])
    else:
        # Nuvem/container: bind convencional (ex.: 0.0.0.0:$PORT).
        print(f"[serve] bind {host}:{port}  backend={BACKEND}", flush=True)
        uvicorn.run("app:app", host=host, port=port,
                    log_level=LOGLVL, access_log=False)


if __name__ == "__main__":
    main()
