# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R719 — Aquisição sem executar.

Hermético: subprocess mockado; intenções sintéticas em tmp.
"""
import json
import os
from unittest import mock

import pytest


def _int_aprovada(tmp_path, url="https://github.com/pgmpy/pgmpy"):
    base = tmp_path / "int"
    base.mkdir(exist_ok=True)
    (base / "intencoes.json").write_text(json.dumps({
        "intencoes": [{"intencao_id": "INT-X", "url": url, "classe": "ativo", "status": "aprovada"}],
        "retidas_informativas": []}), encoding="utf-8")
    return str(base)


def _proc_ok():
    m = mock.Mock()
    m.returncode = 0
    m.stdout = ""
    m.stderr = ""
    return m


def test_fora_allowlist_sem_subprocesso(tmp_path):
    from integrations import polymath_aquisicao as aq
    d = _int_aprovada(tmp_path)
    with mock.patch("subprocess.run") as s:
        with pytest.raises(ValueError):
            aq.clonar_auditado("https://github.com/evil/hack", str(tmp_path / "c"), True, intencoes_dir=d)
        assert not s.called


def test_sem_consentimento_e_sem_aprovacao(tmp_path):
    from integrations import polymath_aquisicao as aq
    d = _int_aprovada(tmp_path)
    with mock.patch("subprocess.run") as s:
        with pytest.raises(ValueError):
            aq.clonar_auditado("https://github.com/pgmpy/pgmpy", str(tmp_path / "c"), False, intencoes_dir=d)
        assert not s.called
    # intenção aguardando não autoriza
    base2 = tmp_path / "int2"
    base2.mkdir(exist_ok=True)
    (base2 / "intencoes.json").write_text(json.dumps({
        "intencoes": [{"intencao_id": "INT-Y", "url": "https://github.com/pgmpy/pgmpy", "status": "aguardando_humano"}],
        "retidas_informativas": []}), encoding="utf-8")
    with mock.patch("subprocess.run") as s2:
        with pytest.raises(ValueError):
            aq.clonar_auditado("https://github.com/pgmpy/pgmpy", str(tmp_path / "c"), True, intencoes_dir=str(base2))
        assert not s2.called


def test_clone_ok_com_head(tmp_path):
    from integrations import polymath_aquisicao as aq
    d = _int_aprovada(tmp_path)
    dest_base = str(tmp_path / "clones")
    def falso_run(cmd, **kw):
        assert cmd[:4] == ["git", "clone", "--depth", "1"]
        alvo = cmd[5]
        os.makedirs(os.path.join(alvo, ".git"), exist_ok=True)
        with open(os.path.join(alvo, ".git", "HEAD"), "w", encoding="utf-8") as fh:
            fh.write("ref: refs/heads/main\n")
        return _proc_ok()
    with mock.patch("subprocess.run", side_effect=falso_run) as s:
        r = aq.clonar_auditado("https://github.com/pgmpy/pgmpy", dest_base, True, intencoes_dir=d)
        assert r["adquirido"] is True and r["head_legivel"] is True
        assert len(r["sha256_head"]) == 64
        assert s.called


def test_overrides_suprem_licenca(tmp_path):
    from integrations import polymath_readiness as rd
    base = tmp_path / "int"
    base.mkdir(exist_ok=True)
    (base / "intencoes.json").write_text(json.dumps({
        "intencoes": [{"intencao_id": "INT-Z", "url": "https://github.com/sympy/sympy",
                       "classe": "formal-estavel", "status": "aprovada"}],
        "retidas_informativas": []}), encoding="utf-8")
    clones = tmp_path / "clones" / "sympy__sympy" / ".git"
    clones.mkdir(parents=True)
    (clones / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    pins = [{"url": "https://github.com/sympy/sympy", "commit": "a" * 40, "federavel": True,
             "motivo": "ok", "license": None, "license_ok": False, "archived": False}]
    ov = {"https://github.com/sympy/sympy": {"licenca": "BSD", "url_license": "https://x",
          "sha256_license": "b" * 64, "confirmado_por": "op"}}
    r = rd.avaliar(str(base), pins, str(tmp_path / "clones"), overrides=ov)
    assert r["avaliadas"][0]["pronto_para_R621"] is True


def test_sem_execucao_no_modulo():
    import integrations.polymath_aquisicao as mod
    src = open(mod.__file__, encoding="utf-8").read()
    for proibido in ("pip install", "docker run", "npm install", "Popen(", "os.system("):
        assert proibido not in src
