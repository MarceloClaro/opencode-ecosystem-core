"""SPEC-935-R878 — servidor dual-stack (IPv4 + IPv6) da reprodução RX.

Valida o launcher `outputs/core-r853-rx/repro/serve.py`: o socket único
AF_INET6 em [::] com IPV6_V6ONLY=0 aceita conexões IPv4 (mapeadas) **e**
IPv6 simultaneamente — a lacuna que o `uvicorn --host` não cobre.
"""

from __future__ import annotations

import importlib.util
import socket
import threading
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1] / "outputs" / "core-r853-rx" / "repro"


def _load_serve():
    spec = importlib.util.spec_from_file_location("rx_serve", REPRO / "serve.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_launcher_existe():
    assert (REPRO / "serve.py").is_file()


def test_dualstack_socket_v6only_desligado():
    mod = _load_serve()
    s = mod._dualstack_socket(0)
    try:
        assert s.family == socket.AF_INET6
        assert s.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY) == 0
    finally:
        s.close()


def test_dualstack_aceita_ipv4_e_ipv6():
    mod = _load_serve()
    s = mod._dualstack_socket(0)
    port = s.getsockname()[1]
    aceitos: list[str] = []

    def _accept():
        for _ in range(2):
            try:
                conn, addr = s.accept()
                aceitos.append(addr[0])
                conn.close()
            except OSError:
                return

    t = threading.Thread(target=_accept, daemon=True)
    t.start()
    # IPv4 (vira ::ffff:127.0.0.1 no socket AF_INET6 dual-stack)
    c4 = socket.create_connection(("127.0.0.1", port), timeout=5)
    c4.close()
    # IPv6 nativo
    c6 = socket.create_connection(("::1", port), timeout=5)
    c6.close()
    t.join(timeout=5)
    s.close()

    assert len(aceitos) == 2, f"esperava 2 conexões, veio {len(aceitos)}: {aceitos}"


def test_porta_default_8799(monkeypatch):
    mod = _load_serve()
    assert mod.PORT == 8799
    assert str(mod.BACKEND).endswith("repro/backend")
