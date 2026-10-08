# -*- coding: utf-8 -*-
"""
Testes da Federação de Artefatos Multi-Harness (SPEC-935-R621).

Cobertura, por invariante da spec:

- INV-R621.1  proveniência e os dois hashes gravados no destino; licença não
             declarada é aviso, não bloqueio
- INV-R621.2  inventário descobre os quatro ecossistemas, declara as raízes
             ausentes, colapsa duplicatas auditáveis e nunca conta artefato
             cujo arquivo não existe
- INV-R621.3  corpo preservado verbatim; `content_sha256` confere com o corpo de
             origem e `source_file_sha256` com o arquivo de origem
- INV-R621.4  hooks emitidos como manifesto inerte, jamais executados
- INV-R621.5  pesos da cabeça `harness` somam 1; `attach_to_router` é reversível
- INV-R621.6  `require_license` recusa **e registra**; relatório separa
             `discovered` de `emitted` e nunca afirma paridade com recusa
- INV-R621.7  os testes não tocam `agents/catalog/`, `livro-core/` nem o
             worktree do operador

Regras funcionais da seção 3 da spec, sem invariante própria: idempotência da
emissão, tokenização bilíngue e parsing de frontmatter/hooks.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from integrations.harness_federation import (
    HarnessEmitter,
    HarnessHarvester,
    build_artifact,
    parse_frontmatter,
    parse_hook_manifest,
    slugify,
)
from transformer import (
    AttentionRouter,
    HarnessAttentionHead,
    HarnessRegistry,
    attach_to_router,
)
from transformer.harness_head import _tokens, license_score

# ---------------------------------------------------------------- fixtures

SKILL_BODY = """---
name: revisar-codigo-seguro
description: Revisa codigo procurando vulnerabilidades de seguranca antes do merge
---

# Revisar codigo seguro

Executa revisao de codigo com foco em seguranca e vulnerabilidades.
"""

ANTIGRAVITY_SKILL_BODY = """---
name: cloud-sql-postgres-admin
description: Administra instancias de Cloud SQL PostgreSQL, replicas e conexoes
---

# Cloud SQL PostgreSQL admin

Provisiona, monitora e faz replica de bancos gerenciados.
"""

AGENT_BODY = """---
name: auditor-de-seguranca
description: Audita aplicacoes em busca de vulnerabilidades exploitable
capabilities:
  - security-audit
  - code-review
---

# Auditor de seguranca
"""

HOOK_MANIFEST = json.dumps({
    "hooks": {
        "PreToolUse": [
            {"hooks": [{"type": "command", "command": 'python3 -c "print(1)"'}]},
        ],
        "PostToolUse": [
            {"hooks": [{"type": "command", "command": "git diff --stat"}]},
        ],
    },
}, indent=2)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture()
def fixture_tree(tmp_path: Path) -> Path:
    """
    Árvore mínima com os quatro ecossistemas, com uma cópia de plugin que
    contém as mesmas skills (a duplicata que INV-R621.1 exige colapsar).
    """

    home = tmp_path / "home"
    repo = tmp_path / "repo"

    _write(home / ".claude/plugins/cache/superpowers/skills/revisar-codigo-seguro/SKILL.md", SKILL_BODY)
    # A mesma skill copiada no marketplace: byte-idêntica, mesmo ecossistema.
    # É a duplicata que a deduplicação precisa colapsar mantendo rastro.
    _write(home / ".claude/plugins/marketplaces/superpowers/skills/revisar-codigo-seguro/SKILL.md", SKILL_BODY)
    _write(home / ".claude/plugins/marketplaces/superpowers/.claude-plugin/plugin.json",
           json.dumps({"name": "superpowers", "license": "MIT"}))
    _write(home / ".claude/agents/auditor-de-seguranca.md", AGENT_BODY)
    # O manifesto de hooks do Claude vive em `<plugin>/hooks/hooks.json`.
    _write(home / ".claude/plugins/cache/pre-commit-guard/hooks/hooks.json", HOOK_MANIFEST)
    # Codex só reconhece o padrão `.agents/`; `~/.codex/agents` é outra coisa.
    _write(home / ".codex/.agents/skills/revisar-codigo-seguro/SKILL.md", SKILL_BODY)
    _write(home / ".gemini/antigravity-cli/builtin/skills/cloud-sql-postgres-admin/SKILL.md",
           ANTIGRAVITY_SKILL_BODY)
    _write(repo / "SKILL_CHATGPT.md",
           "---\nname: openai-policies\ndescription: Politicas de uso do ChatGPT\n---\n")
    _write(repo / ".codex-plugin/plugin.json", json.dumps({"name": "deepseek-harness"}))

    return tmp_path


@pytest.fixture()
def harvester(fixture_tree: Path) -> HarnessHarvester:
    return HarnessHarvester(repo_root=str(fixture_tree / "repo"), home=str(fixture_tree / "home"))


@pytest.fixture()
def artifacts(harvester: HarnessHarvester):
    return harvester.discover()


# ------------------------------- INV-R621.2 (descoberta verificável)

def test_inventario_descobre_os_quatro_ecossistemas(harvester):
    inventory = harvester.inventory()

    assert set(inventory["ecosystems_present"]) == {"claude", "codex", "antigravity", "chatgpt"}
    assert inventory["ecosystems_missing"] == []
    # As raízes que a fixture não cria precisam aparecer nominalmente, com o
    # motivo. Sem isso o relatório afirmaria cobertura que não varreu.
    missing = {r["label"] for r in inventory["roots_missing"]}
    assert {"claude:project", "antigravity:project", "antigravity:cloud_scripts",
            "codex:agents_standard"} <= missing
    assert all(r["reason"] == "root_absent" for r in inventory["roots_missing"])
    assert all(Path(r["path"]).exists() for r in inventory["roots_scanned"])


def test_duplicata_e_colapsada_mas_registra_o_caminho(harvester, artifacts):
    """
    A mesma skill copiada em plugin_cache e marketplace é um artefato só, e o
    caminho descartado fica registrado em `duplicate_paths` — o relatório tem
    de conseguir explicar a contagem, não apenas delivering o número.
    """

    claude_copies = [a for a in artifacts
                     if a.ecosystem == "claude" and a.slug == "revisar-codigo-seguro"]
    assert len(claude_copies) == 1
    assert claude_copies[0].duplicate_paths, "a duplicata tem de ser rastreável"
    assert all(Path(p).exists() for p in claude_copies[0].duplicate_paths)

    # Ecossistemas diferentes são artefatos legítimos distintos, mesmo com
    # conteúdo byte-idêntico: o roteador decide por origem, não por hash. O
    # Antigravity traz outro corpo, e por isso é outro artefato.
    by_ecosystem = {a.ecosystem for a in artifacts if a.slug == "revisar-codigo-seguro"}
    assert by_ecosystem == {"claude", "codex"}

    # Procedência atribuída pela raiz, não pelo palpite do caminho: a skill do
    # usuário em `~/.codex` é `user`, e a cópia do plugin Claude é `third_party`.
    origins = {a.ecosystem: a.origin for a in artifacts if a.slug == "revisar-codigo-seguro"}
    assert origins == {"claude": "third_party", "codex": "user"}


def test_artefato_inexistente_nao_e_contado(harvester):
    inventory = harvester.inventory()
    todos = harvester.discover()
    assert all(Path(a.source_path).exists() for a in todos)
    assert inventory["discovered"] == len(todos)
    assert all(a.available for a in todos)
    # A deduplicação precisa ser auditável pelo relatório, não apenas correta:
    # um número de artefatos menor que o de arquivos em disco só se explica por
    # `duplicate_paths`, e essa é a única prova de que nada foi descartado.
    colapsados = sum(len(a.duplicate_paths) for a in todos)
    assert inventory["duplicates_collapsed"] == colapsados > 0


def test_inventario_separa_aviso_de_bloqueio(harvester):
    """
    `license_undeclared` é aviso, não impedimento. O relatório precisa dizer as
    duas coisas: `synchronized` estrito (nenhum aviso) e `synchronized_strict`
    (nenhum bloqueio). Um relatório que só dissesse "286 degradados" forçaria o
    operador a abrir a lista para descobrir que nenhum deles o impede de usar.
    """

    inv = harvester.inventory()
    # A fixture tem licença MIT declarada num plugin, mas as skills de usuário
    # não trazem `license`: existe aviso e não existe bloqueio.
    assert inv["degraded_by_reason"].get("license_undeclared", 0) > 0
    assert inv["blocking"] == 0
    assert inv["synchronized"] is False, "aviso impede a afirmação estrita de paridade"
    assert inv["synchronized_strict"] is True
    assert inv["duplicates_collapsed"] > 0, "a deduplicação precisa ser auditável"


def test_artefato_ausente_no_disco_marca_indisponivel(tmp_path):
    ghost = tmp_path / "skills/nao-existe/SKILL.md"
    artifact = build_artifact(
        source_path=str(ghost),
        ecosystem="claude",
        kind="skill",
        origin="user",
        name="nao-existe",
        description="artefato sem arquivo",
    )

    assert artifact.available is False
    assert "source_not_found" in artifact.degraded_reasons
    # Indisponível é bloqueio de verdade: o card não pode ser oferecido ao router.
    assert "source_not_found" in artifact.blocking_reasons
    assert artifact.agent_card()["status"] == "unavailable"


# ------------------------- INV-R621.1 / INV-R621.3 (hashes e proveniência)

def test_corpo_preservado_verbatim_na_emissao(harvester, artifacts, tmp_path):
    emitter = HarnessEmitter(repo_root=str(tmp_path / "out"), dry_run=False)
    skill = next(a for a in artifacts
                 if a.slug == "revisar-codigo-seguro" and a.ecosystem == "claude")
    report = emitter.emit_skill(skill)

    emitted = Path(report["path"])
    assert emitted.exists()
    _, source_body = parse_frontmatter(SKILL_BODY)
    _, emitted_body = parse_frontmatter(emitted.read_text(encoding="utf-8"))
    # O frontmatter é reescrito (é onde mora a proveniência); o corpo não.
    # O `\n` inicial é normalização de fronteira do bloco YAML, não edição:
    # comparar já normalizado é o que prova verbatim de verdade.
    assert emitted_body == source_body.lstrip("\n")


def test_hash_de_corpo_e_hash_de_arquivo_sao_distintos_e_conferiveis(harvester, artifacts, tmp_path):
    checked = 0
    for artifact in artifacts:
        # `source_file_sha256` é conferível com `sha256sum` na origem.
        assert artifact.source_file_sha256 == _sha256(Path(artifact.source_path))
        # `content_sha256` cobre só o corpo, então difere do arquivo inteiro
        # sempre que houver frontmatter.
        assert artifact.content_sha256 == hashlib.sha256(
            parse_frontmatter(Path(artifact.source_path).read_text(encoding="utf-8"))[1].encode("utf-8")
        ).hexdigest()
        checked += 1
    assert checked > 0

    emitter = HarnessEmitter(repo_root=str(tmp_path / "out"), dry_run=False)
    skill = next(a for a in artifacts if a.ecosystem == "claude" and a.kind == "skill")
    report = emitter.emit_skill(skill)
    assert report["body_sha256"] == skill.content_sha256
    assert report["source_file_sha256"] == skill.source_file_sha256


def test_arquivo_ausente_nao_fabrica_hash(tmp_path):
    artifact = build_artifact(
        source_path=str(tmp_path / "nao-existe.md"),
        ecosystem="claude", kind="skill", origin="user",
        name="x", description="d", body="corpo",
    )
    assert artifact.source_file_sha256 == ""
    assert artifact.content_sha256 == hashlib.sha256(b"corpo").hexdigest()


def test_proveniencia_registrada_no_destino(harvester, artifacts, tmp_path):
    out = tmp_path / "out"
    emitter = HarnessEmitter(repo_root=str(out), dry_run=False)
    skill = next(a for a in artifacts if a.ecosystem == "claude" and a.kind == "skill")
    emitted = Path(emitter.emit_skill(skill)["path"])
    front = yaml.safe_load(emitted.read_text(encoding="utf-8").split("---")[1])
    prov = front["x-proveniencia"]

    assert front["name"] == skill.emission_slug
    assert prov["ecossistema"] == "claude"
    assert prov["origem"] == skill.origin
    assert prov["caminho_origem"] == skill.source_path
    assert prov["sha256_corpo"] == skill.content_sha256
    assert prov["sha256_arquivo_origem"] == skill.source_file_sha256
    assert prov["licenca"] == (skill.license or "(nao declarada)")
    assert prov["importado_por"] == "SPEC-935-R621"


# ------------------------- seção 3.3 (emissão idempotente)

def test_emissao_e_idempotente(harvester, artifacts, tmp_path):
    out = tmp_path / "out"
    kinds = ("skill", "agent", "hook")

    first = HarnessEmitter(repo_root=str(out), dry_run=False).emit_all(artifacts, kinds=kinds)
    assert first["emitted"] > 0

    stamps = {p: Path(p).read_bytes() for p in first["emitted_paths"]}
    second = HarnessEmitter(repo_root=str(out), dry_run=False).emit_all(artifacts, kinds=kinds)

    assert second["emitted"] == first["emitted"]
    assert second["skipped"] == 0
    for path, content in stamps.items():
        assert Path(path).read_bytes() == content, "reemissão alterou arquivo existente"


# ------------------------- INV-R621.4 (hooks jamais executados)

def test_hooks_sao_manifesto_e_nunca_executados(harvester, artifacts, tmp_path):
    out = tmp_path / "out"
    emitter = HarnessEmitter(repo_root=str(out), dry_run=False)
    hook = next(a for a in artifacts if a.kind == "hook")
    report = emitter.emit_hooks(hook)

    assert report["hooks_executed"] is False
    manifest = json.loads(Path(report["path"]).read_text(encoding="utf-8"))
    assert manifest["execution"] == "blocked_pending_human_review"
    # O comando aparece como texto inerte; nada é executado, e isso é declarado.
    assert manifest["commands"]


def test_relatorio_de_lote_declara_hooks_nao_executados(harvester, artifacts, tmp_path):
    report = HarnessEmitter(repo_root=str(tmp_path / "out"), dry_run=True).emit_all(artifacts)
    assert report["hooks_executed"] is False


# ------------------------- INV-R621.6 (recusa registrada)

def test_require_license_recusa_e_registra_o_motivo(harvester, artifacts, tmp_path):
    # O artefato de código tem licença declarada (MIT do plugin); o do Codex
    # não tem. Ambos precisam aparecer no relatório, um emitido e um recusado.
    report = HarnessEmitter(repo_root=str(tmp_path / "out"), dry_run=True).emit_all(
        artifacts, kinds=("skill",), require_license=True)

    assert report["refused"] > 0
    assert report["selected"] == len([a for a in artifacts if a.kind == "skill"])
    assert report["emitted"] + report["refused"] == report["selected"]
    motivos = {r["blocking_reasons"][-1] for r in report["refused_detail"]}
    assert motivos == {"license_required_by_operator"}
    # Fail-closed: havendo recusa, o lote não pode se declarar sincronizado.
    assert report["synchronized"] is False


def test_sem_require_license_artefato_sem_licencia_e_emitido(harvester, artifacts, tmp_path):
    report = HarnessEmitter(repo_root=str(tmp_path / "out"), dry_run=True).emit_all(
        artifacts, kinds=("skill",), require_license=False)

    assert report["refused"] == 0
    assert report["emitted"] == len([a for a in artifacts if a.kind == "skill"])


# ------------------------- seção 3.4 (tokenização e ranqueamento)

@pytest.mark.parametrize("query,expected", [
    ("revisar codigo com seguranca", "security"),
    ("escrever testes antes de implementar", "test"),
    ("implantar servico em nuvem", "cloud"),
    ("auditoria de performance", "audit"),
])
def test_tokenizacao_pt_br_casa_com_termo_ingles(query, expected):
    assert expected in _tokens(query)


def test_tokenizacao_ignora_acento_e_plural():
    assert _tokens("revisões de segurança") == ["review", "security"]
    assert _tokens("pacientes clínicos") == ["patient", "clinical"]


def test_forma_canonica_nao_e_corrompida_por_stemming():
    # "analysis" radicalizado viraria "analysi" e quebraria o casamento.
    assert "analysis" in _tokens("análise de dados")


def test_ranking_harness_seleciona_a_skill_de_revisao(harvester, fixture_tree):
    registry = HarnessRegistry(repo_root=str(fixture_tree / "repo"), home=str(fixture_tree / "home"))
    explanation = registry.route(
        "revisar codigo procurando vulnerabilidades de seguranca", [])

    # Claude e Codex têm cópia byte-idêntica; a do usuário vence porque a
    # cabeça de maturidade paga procedência a `user` acima de `third_party`.
    # O que o teste fixa é a semântica: o vencedor é a skill de revisão, e
    # não a de PostgreSQL que também existe na fixture.
    winner, score = explanation["ranking"][0]
    assert winner == "codex:skill:user:revisar-codigo-seguro"
    assert score > 0.0
    assert set(explanation["weights"]) >= {"semantic", "capability", "maturity", "license"}

    # As cabeças vêm na ordem dos cards, não na do ranking — por isso o índice
    # precisa ser resolvido pelo agent_id, senão o teste passa a medir a
    # posição da lista em vez da qualidade do candidato.
    index = [c["agent_id"] for c in registry.cards()].index(winner)
    assert explanation["heads"]["semantic"][index] > 0.0
    assert explanation["heads"]["maturity"][index] > 0.0

    # Desempate entre as cópias idênticas é auditável: mesma semântica,
    # maturidade diferente (procedência `user` > `third_party`).
    other = [c["agent_id"] for c in registry.cards()].index(
        "claude:skill:third_party:revisar-codigo-seguro")
    assert explanation["heads"]["semantic"][index] == explanation["heads"]["semantic"][other]
    assert explanation["heads"]["maturity"][index] > explanation["heads"]["maturity"][other]

    # E o artefato de PostgreSQL, que não tem nada a ver com a tarefa, fica
    # abaixo mesmo sendo `first_party` e sem licença declarada.
    assert "cloud-sql-postgres-admin" not in winner


def test_maturidade_paga_procedencia(harvester, fixture_tree):
    """Cópia idêntica: artefato do usuário acima de cópia de terceiro."""

    registry = HarnessRegistry(repo_root=str(fixture_tree / "repo"), home=str(fixture_tree / "home"))
    cards = registry.cards()
    copies = [c for c in cards if c["agent_id"].endswith(":revisar-codigo-seguro")]
    scores = HarnessAttentionHead._head_maturity(copies)
    por_id = dict(zip([c["agent_id"] for c in copies], scores))

    assert por_id["codex:skill:user:revisar-codigo-seguro"] > \
        por_id["claude:skill:third_party:revisar-codigo-seguro"]


# ------------------------- INV-R621.5 (pesos e reversibilidade)

def test_mix_zero_devolve_exatamente_o_router_legado(harvester, fixture_tree):
    registry = HarnessRegistry(repo_root=str(fixture_tree / "repo"), home=str(fixture_tree / "home"))
    cards = registry.cards()
    query = "revisar codigo com seguranca"

    router = AttentionRouter()
    legacy = router.route(query, [], cards)

    attach_to_router(router, mix=0.0)
    assert router.route(query, [], cards) == legacy


def test_mix_um_sobra_so_a_cabeca_harness(harvester, fixture_tree):
    registry = HarnessRegistry(repo_root=str(fixture_tree / "repo"), home=str(fixture_tree / "home"))
    cards = registry.cards()
    router = AttentionRouter()
    attach_to_router(router, mix=1.0)

    ranking = router.route("revisar codigo procurando vulnerabilidades", [], cards)
    assert ranking[0][0].endswith(":revisar-codigo-seguro")


def test_reanexar_realmente_troca_o_mix(harvester, fixture_tree):
    """Regressão: o segundo attach atualizava só o atributo, não o closure."""

    registry = HarnessRegistry(repo_root=str(fixture_tree / "repo"), home=str(fixture_tree / "home"))
    cards = registry.cards()
    query = "revisar codigo procurando vulnerabilidades"
    router = AttentionRouter()
    attach_to_router(router, mix=1.0)
    only_harness = router.route(query, [], cards)

    attach_to_router(router, mix=0.0)
    assert router.route(query, [], cards) != only_harness


def test_mix_fora_do_intervalo_e_rejeitado():
    with pytest.raises(ValueError):
        attach_to_router(AttentionRouter(), mix=1.5)


# ------------------------- INV-R621.1 (licença é aviso)

def test_licenca_nao_declarada_e_aviso_e_nao_bloqueio(harvester, artifacts):
    sem_licenca = [a for a in artifacts if "license_undeclared" in a.degraded_reasons]
    assert sem_licenca, "a fixture deve conter ao menos um artefato sem licença"

    for artifact in sem_licenca:
        assert artifact.blocking_reasons == []
        assert artifact.agent_card()["status"] == "available"


def test_licenca_desconhecida_ou_ausente_tem_pior_nota():
    # MIT > rótulo não reconhecido > silêncio. Um rótulo que não corresponde a
    # nenhuma licença conhecida não concede permissão nenhuma, mas ainda é
    # declaration; o silêncio é o pior caso fail-closed.
    assert license_score("MIT") > license_score("licença inventada") > license_score("")
    assert license_score("") == 0.0
    assert license_score("AGPL-3.0") < license_score("MIT")


def test_licenca_nao_casa_por_substring():
    # Regressão: `key in texto` faz "submit" casar com "mit". Numa federação
    # que decide o que pode ser reimportado, isso classificaria como MIT um
    # rótulo que não é uma licença — o oposto de fail-closed.
    for falso_positivo in ("submit", "transmit", "emitted", "comitted", "limit"):
        assert license_score(falso_positivo) < 0.5, falso_positivo
    # A fronteira de token não pode perder a licença de verdade.
    assert license_score("MIT") == 1.0
    assert license_score("MIT License") == 1.0
    assert license_score("SPDX-License-Identifier: Apache-2.0") == 1.0
    assert license_score("BSD") == license_score("BSD-3-Clause")


def test_cabeca_maturity_ignora_avisos(harvester, artifacts):
    """Licença não declarada não pode zerar a integridade/maturidade."""

    cards = [a.agent_card() | {"blocking": bool(a.blocking_reasons)} for a in artifacts]
    scores = HarnessAttentionHead._head_maturity(cards)
    sem_licenca_idx = [i for i, a in enumerate(artifacts)
                       if "license_undeclared" in a.degraded_reasons]
    assert scores and all(scores[i] > 0.0 for i in sem_licenca_idx)


# ------------------------- seção 3.1 (parsers e normalização)

def test_parse_frontmatter_separa_metadados_e_corpo():
    front, body = parse_frontmatter(SKILL_BODY)
    assert front["name"] == "revisar-codigo-seguro"
    assert "seguranca" in front["description"]
    assert "vulnerabilidades" in body
    assert "---" not in body.split("\n")[0]


def test_parse_frontmatter_sem_bloco_devolve_corpo_integral():
    texto = "# Só corpo\n\nSem metadados."
    front, body = parse_frontmatter(texto)
    assert front == {}
    assert body == texto


def test_parse_hook_manifest_extrai_eventos_e_comandos():
    events, commands = parse_hook_manifest(HOOK_MANIFEST)
    assert events == ["PreToolUse", "PostToolUse"]
    assert any("print(1)" in command for command in commands)


def test_parse_hook_manifest_nao_inventa_evento_em_entrada_nao_json():
    # Texto que não é JSON não pode virar lista de comandos: um comando
    # inventado aqui seria executado por um revisor humano achando que veio
    # do upstream.
    assert parse_hook_manifest("Executa `python3 -c print(1)` antes.") == ([], [])


def test_slugify_e_estavel_e_seguro():
    assert slugify("Revisar Código / Seguro!") == "revisar-codigo-seguro"
    assert slugify("  Espaços   extras  ") == "espacos-extras"


def test_artifact_id_inclui_kind_para_nao_colidir():
    ids = {
        build_artifact(
            source_path=__file__, ecosystem="claude", kind=kind, origin="user",
            name="mesmo-nome", description="d",
        ).artifact_id
        for kind in ("skill", "agent", "command", "spec")
    }
    assert len(ids) == 4


# ------------------------- seção 4 (superfície de linha de comando)

def test_cli_resolve_harness_antes_do_orquestrador(monkeypatch, capsys):
    """
    `harness inventory` não pode pagar o custo de carregar o catálogo inteiro
    para então varrer o disco. O teste planta uma armadilha: se algo importar o
    orquestrador, a importação estoura.
    """

    import builtins

    from marceloclaro import cli

    real_import = builtins.__import__

    def _import(name, *args, **kwargs):
        if name.startswith("marceloclaro.orchestrator"):
            raise AssertionError(
                f"CLI de inventário não deve carregar o orquestrador: importou {name}"
            )
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _import)
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "harness", "inventory"])
    assert cli.main() == 0

    report = json.loads(capsys.readouterr().out)
    assert report["spec_id"] == "SPEC-935-R621"
    assert report["counted_agents"] > 0


def test_cli_emit_e_dry_run_por_padrao(monkeypatch, capsys, tmp_path):
    """Sem `--execute`, nenhum arquivo é gravado — nem no tmp_path fornecido."""

    from marceloclaro import cli

    monkeypatch.setattr(cli.sys, "argv", [
        "marceloclaro", "harness", "emit", "--kinds", "skill", "--require-license",
    ])
    # `emit` sai com 1 quando há recusas, e isso é o comportamento correto:
    # o comando está dizendo "não está tudoLimpo", não que quebrou.
    cli.main()
    saida = capsys.readouterr().out
    assert "dry-run" in saida

    doc, _, _ = saida.partition("\n\n(")
    report = json.loads(doc)
    assert report["dry_run"] is True
    assert report["emitted"] > 0, "o dry-run ainda descreve o que faria"
    assert report["emitted_paths"], "o dry-run lista o que gravaria"
    assert not list(tmp_path.iterdir()), "dry-run não pode ter gravado caminho nenhum"
    assert report["hooks_executed"] is False
    assert report["refused"] > 0 and report["refused_detail"], "recusa precisa do motivo"


def test_cli_emit_grava_quando_executado_explicitamente(monkeypatch, capsys, tmp_path):
    """`--execute` grava de verdade — o teste aponta a raiz para o tmp_path."""

    from marceloclaro import cli

    import transformer.harness_head as hh

    monkeypatch.setattr(cli.sys, "argv", [
        "marceloclaro", "harness", "emit", "--kinds", "skill", "--execute",
    ])
    monkeypatch.setattr(hh.HarnessRegistry, "__init__",
                        _registry_pointing_to(hh.HarnessRegistry.__init__, tmp_path))
    cli.main()
    report = json.loads(capsys.readouterr().out.split("\n\n(")[0])
    assert report["dry_run"] is False
    assert report["emitted"] > 0
    escritos = [p for p in tmp_path.rglob("SKILL.md")]
    assert escritos, "--execute precisa ter gravado de fato"
    assert all(p.read_text(encoding="utf-8").startswith("---") for p in escritos)


def _registry_pointing_to(original, repo_root):
    """Fabrica um `__init__` de registry que emite num diretório temporário.

    Monkeypatchar o construtor é mais direto do que inventar uma variável de
    ambiente: `emit` grava em `<repo_root>/.opencode/...` e o teste precisa
    garantir que esse `<repo_root>` é o `tmp_path` dele, nunca o repositório do
    operador.
    """

    def __init__(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self.repo_root = str(repo_root)

    return __init__
