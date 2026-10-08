# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R714 — Executor vivo com consentimento.

Hermético: urllib/subprocess mockados; sem rede real, sem segredo vazado.
"""
import datetime
import io
import json
import os
from unittest import mock

import pytest


def _iso(dias_atras=3):
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=dias_atras)).isoformat()


class _Resp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _proc_ok(stdout="f" * 40 + "\tHEAD\n"):
    m = mock.Mock()
    m.returncode = 0
    m.stdout = stdout
    return m


def test_fetcher_vivo_ok_mockado():
    from integrations import polymath_pinagem_viva as viva
    api = {"pushed_at": _iso(3), "license": {"spdx_id": "MIT"}, "archived": False}
    with mock.patch("urllib.request.urlopen", return_value=_Resp(api)) as u, \
         mock.patch("subprocess.run", return_value=_proc_ok()) as s:
        r = viva.fetcher_vivo("pgmpy", "pgmpy", token="SEGREDO_XYZ")
        assert r["commit"] == "f" * 40 and r["license_ok"] is True
        # Token vai ao header, não ao retorno
        req = u.call_args[0][0]
        assert "SEGREDO_XYZ" in req.get_header("Authorization")
        assert "SEGREDO_XYZ" not in json.dumps(r)
        assert s.called


def test_404_vira_bloqueado_tolerado():
    from integrations import polymath_pinagem as pin
    from integrations import polymath_pinagem_viva as viva
    import urllib.error
    def falso(org, repo):
        if org.lower() == "pgmpy":
            return {"commit": "a" * 40, "pushed_at": _iso(2), "license": "MIT", "license_ok": True, "archived": False}
        raise urllib.error.HTTPError("url", 404, "nf", None, io.BytesIO(b""))
    res = pin.revalidar_todos(falso)
    por = {e["url"].lower(): e for e in res["pins"]}
    assert por["https://github.com/pgmpy/pgmpy"]["federavel"] is True
    assert por["https://github.com/sympy/sympy"]["federavel"] is False
    assert viva  # módulo importável


def test_sem_consentimento_sem_rede():
    from integrations import polymath_pinagem_viva as viva
    with mock.patch("urllib.request.urlopen") as u, mock.patch("subprocess.run") as s:
        with pytest.raises(ValueError):
            viva.executar("/tmp/qualquer", consentimento=False)
        with pytest.raises(ValueError):
            viva.executar("/tmp/qualquer", consentimento="true")
        assert not u.called and not s.called


def test_token_nunca_vazado(tmp_path):
    from integrations import polymath_pinagem_viva as viva
    def falso(org, repo):
        return {"commit": "b" * 40, "pushed_at": _iso(1), "license": "MIT", "license_ok": True, "archived": False}
    out = viva.executar(str(tmp_path), consentimento=True, token="SUPERSEGREDO_123", fetcher=falso)
    assert out["ok"] is True
    for nome in ("labs_pins.json", "federacao_gate.json", "vivo_meta.json"):
        texto = (tmp_path / nome).read_text(encoding="utf-8")
        assert "SUPERSEGREDO_123" not in texto
    meta = json.loads((tmp_path / "vivo_meta.json").read_text(encoding="utf-8"))
    assert meta["token_presente"] is True
    assert meta["consentimento"] is True


def test_cli_dry_run_sem_rede(tmp_path):
    from integrations import polymath_pinagem_viva as viva
    rc = viva.main(["--dest", str(tmp_path), "--consentimento", "true", "--dry-run"])
    assert rc == 0
    assert (tmp_path / "federacao_gate.json").exists()
    rc2 = viva.main(["--dest", str(tmp_path), "--consentimento", "false", "--dry-run"])
    assert rc2 == 2
