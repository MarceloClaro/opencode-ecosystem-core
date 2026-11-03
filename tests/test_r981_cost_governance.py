# -*- coding: utf-8 -*-
"""Governança de custo de tokens multi-superfície (SPEC-981).

O Core executa em seis superfícies de inferência (Ollama/NVIDIA on-device,
OpenCode Zen/Go, Gemini, OpenAI, Antigravity) com semânticas de custo
heterogêneas: token cobrado, cota de assinatura, tier gratuito ou compute
local. Antes desta spec não existia registro de tarifas nem contabilidade: o
comando ``economy`` do Core mede *stakes* da token economy (garantia de
comportamento), não dinheiro.

Estes testes são o gate. Eles falham no baseline (o módulo não existe) e só
passam com a implementação completa.
"""

from __future__ import annotations

import json
import os

import pytest

from integrations.cost_governance import (
    COMPLEXITIES,
    CostRegistryError,
    Usage,
    agent_chain,
    complexity_for_agent,
    estimate_cost,
    is_free_model,
    list_surfaces,
    load_registry,
    rank_models,
    resolve_plan,
    surface_ids,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def registro():
    return load_registry()


@pytest.fixture()
def ledger(tmp_path):
    from integrations.cost_governance import BudgetLedger

    return BudgetLedger(path=tmp_path / "ledger.jsonl")


# ── CA1 — registro declarado ─────────────────────────────────────────────────

class TestRegistro:
    def test_registro_carrega_com_tarifas_declaradas(self, registro):
        assert registro["surfaces"], "registro sem superfícies"
        assert registro["tariffs"], "registro sem tarifas"
        assert registro["provenance"]["primary"]["url"], "tarifa sem procedência"

    def test_cobre_as_seis_superficies_do_operador(self, registro):
        ids = set(registro["surfaces"])
        for familia in ("ollama", "nvidia", "opencode", "gemini", "openai", "antigravity"):
            assert any(familia in i for i in ids), (
                f"superfície da família '{familia}' ausente do registro: {sorted(ids)}"
            )

    def test_toda_superficie_declara_o_tipo_de_cobranca(self, registro):
        validos = {"local_compute", "free_tier", "metered_api", "subscription"}
        for sid, meta in registro["surfaces"].items():
            assert meta["kind"] in validos, f"{sid}: tipo de cobrança inválido"
            assert isinstance(meta["billable"], bool), f"{sid}: 'billable' não é booleano"

    def test_toda_tarifa_declara_fonte_e_data(self, registro):
        for chave, tarifa in registro["tariffs"].items():
            assert tarifa.get("source"), f"{chave}: tarifa sem fonte"
            assert tarifa.get("source_date"), f"{chave}: tarifa sem data de consulta"
            for campo in ("input", "output"):
                assert tarifa[campo] is None or tarifa[campo] >= 0, (
                    f"{chave}: tarifa negativa em '{campo}'"
                )

    def test_registro_malformado_falha_fechado(self, tmp_path):
        ruim = tmp_path / "ruim.json"
        ruim.write_text(
            json.dumps({"surfaces": {"x": {"kind": "desconhecido"}}}), encoding="utf-8"
        )
        with pytest.raises(CostRegistryError):
            load_registry(path=ruim)

    def test_tarifa_sem_fonte_e_rejeitada(self, tmp_path):
        ruim = tmp_path / "ruim.json"
        ruim.write_text(
            json.dumps({
                "surfaces": {"s": {"kind": "metered_api", "billable": True}},
                "tariffs": {"s::m": {"input": 1.0, "output": 1.0}},
            }),
            encoding="utf-8",
        )
        with pytest.raises(CostRegistryError):
            load_registry(path=ruim)


# ── CA2 — gratuidade declarada ───────────────────────────────────────────────

class TestGratuidade:
    def test_superficie_local_e_gratuita_em_token(self, registro):
        assert is_free_model("local-ollama", "llama3.2") is True
        assert is_free_model("local-litert-lm", "litert-community/gemma-4-E2B-it-litert-lm") is True

    def test_modelo_free_publicado_e_gratuito(self, registro):
        assert is_free_model("opencode-zen", "mimo-v2.6-flash-free") is True
        assert is_free_model("nvidia-nim", "minimaxai/minimax-m3.1-flash") is True

    def test_modelo_pago_nao_e_gratuito(self, registro):
        assert is_free_model("opencode-go", "mimo-v2.6-flash") is False
        assert is_free_model("opencode-go", "kimi-k3") is False

    def test_modelo_desconhecido_nao_e_gratuito(self, registro):
        """Desconhecido é desconhecido: jamais 'gratuito' por omissão."""
        assert is_free_model("opencode-go", "modelo-que-nao-existe") is False


# ── CA3 — estimativa ─────────────────────────────────────────────────────────

class TestEstimativa:
    def test_estimativa_conferida_a_mao(self):
        """1M entrada com 80% em cache + 100k saída no mimo-v2.6-flash (Go)."""
        uso = Usage(input_tokens=1_000_000, output_tokens=100_000, cached_input_tokens=800_000)
        est = estimate_cost("opencode-go", "mimo-v2.6-flash", uso)
        assert est.usd is not None
        assert est.usd == pytest.approx(0.0582, abs=1e-4)

    def test_estimativa_marca_estimativa_e_proveniencia(self):
        est = estimate_cost(
            "opencode-go", "mimo-v2.6-flash", Usage(input_tokens=1000, output_tokens=1000)
        )
        assert est.is_estimate is True
        assert est.basis == "tariff_declared"
        assert est.source and est.source_date

    def test_tarifa_desconhecida_nao_vira_zero(self):
        est = estimate_cost(
            "opencode-go", "modelo-sem-tarifa", Usage(input_tokens=1000, output_tokens=1000)
        )
        assert est.usd is None
        assert est.basis == "tariff_unknown"
        assert est.is_estimate is False

    def test_superficie_de_assinatura_nao_finge_tarifa_por_token(self):
        est = estimate_cost(
            "antigravity", "qualquer", Usage(input_tokens=1000, output_tokens=1000)
        )
        assert est.usd is None
        assert est.basis == "subscription_quota"
        assert est.caveats

    def test_superficie_local_marca_compute_nao_fatura(self):
        est = estimate_cost("local-ollama", "llama3.2", Usage(input_tokens=1000, output_tokens=1000))
        assert est.usd == 0.0
        assert est.basis == "local_compute"
        assert est.caveats, "compute local não é custo zero de verdade"

    def test_free_tier_por_cota_nao_e_tarifa_por_token(self):
        est = estimate_cost("gemini-cli", "qualquer", Usage(input_tokens=1000, output_tokens=1000))
        assert est.usd is None
        assert est.basis in {"free_tier_quota", "subscription_quota"}


# ── CA4 — ordenação por custo ────────────────────────────────────────────────

class TestOrdenacao:
    def test_rank_ordena_por_custo_blended(self, registro):
        ranked = rank_models(
            "opencode-go", Usage(input_tokens=1_000_000, output_tokens=100_000,
                                  cached_input_tokens=800_000)
        )
        assert ranked, "nenhum modelo com tarifa declarada no provider"
        custos = [c for c, _ in ranked]
        assert custos == sorted(custos), "rank fora de ordem crescente"

    def test_modelo_gratuito_lidera_o_rank(self, registro):
        ranked = rank_models(
            "opencode-zen", Usage(input_tokens=1_000_000, output_tokens=100_000)
        )
        if ranked:
            melhor_id = ranked[0][1]
            assert is_free_model("opencode-zen", melhor_id), (
                f"o rank deveria começar por um modelo gratuito, mas começou por {melhor_id}"
            )


# ── CA5 — complexidade → cadeia ─────────────────────────────────────────────

class TestComplexidade:
    def test_niveis_declarados(self):
        assert COMPLEXITIES == ("trivial", "simples", "media", "complexa", "critica")

    def test_classificacao_por_cartao_real(self):
        assert complexity_for_agent({
            "id": "coder", "category": "engineering",
            "tags": ["python", "debug", "refactor", "implement", "tdd"],
        }) == "media"
        assert complexity_for_agent({
            "id": "auditor", "category": "audit", "tags": ["audit", "metrics"],
        }) == "critica"
        assert complexity_for_agent({
            "id": "academic_writer", "category": "academic",
            "tags": ["academic", "abnt", "imrad", "escrita"],
        }) == "simples"
        assert complexity_for_agent({
            "id": "researcher", "category": "research",
            "tags": ["search", "summarize", "cite", "literature_review", "oa"],
        }) == "complexa"

    def test_classificacao_e_deterministica(self):
        meta = {"id": "x", "category": "engineering", "tags": ["implement"]}
        assert complexity_for_agent(meta) == complexity_for_agent(dict(meta))

    def test_cartao_sem_metadados_nao_quebra(self):
        assert complexity_for_agent({}) in COMPLEXITIES

    def test_cadeia_comeca_pelo_tier_da_complexidade(self):
        cadeia_media = agent_chain("media")
        cadeia_critica = agent_chain("critica")
        assert cadeia_media and cadeia_critica
        assert cadeia_media[0] != cadeia_critica[0]
        assert cadeia_media[0] in cadeia_media

    def test_cadeia_nao_repete_modelo(self):
        for nivel in COMPLEXITIES:
            cadeia = agent_chain(nivel)
            assert len(cadeia) == len(set(cadeia)), f"{nivel}: modelo repetido na cadeia"

    def test_cadeia_termina_em_modelo_capaz(self):
        for nivel in COMPLEXITIES:
            cadeia = agent_chain(nivel)
            assert cadeia[-1].startswith(("opencode-go/", "opencode-zen/")), (
                f"{nivel}: cadeia não termina em modelo capaz: {cadeia[-1]}"
            )


# ── CA6 — plano de superfície ────────────────────────────────────────────────

class TestPlano:
    def test_plano_comeca_por_superficie_gratuita_quando_existe(self):
        plano = resolve_plan("trivial")
        assert plano, "plano vazio"
        assert is_free_model(plano[0].surface_id, plano[0].model_id), (
            f"plano deveria começar por superfície gratuita: {plano[0]}"
        )

    def test_plano_nao_inclui_superficie_sem_tarifa_para_custo(self):
        for passo in resolve_plan("media"):
            assert passo.surface_id in surface_ids()

    def test_plano_de_complexidade_critica_nao_comeca_gratuito(self):
        plano = resolve_plan("critica")
        assert not is_free_model(plano[0].surface_id, plano[0].model_id), (
            "tarefa crítica não pode começar por modelo gratuito sem justificativa"
        )


# ── CA7 — orçamento fail-closed ──────────────────────────────────────────────

class TestOrcamento:
    def test_registra_e_acumula(self, ledger):
        est = estimate_cost("opencode-go", "mimo-v2.6-flash",
                             Usage(input_tokens=1_000_000, output_tokens=100_000))
        ledger.record(est)
        ledger.record(est)
        assert ledger.usage_usd("opencode-go") == pytest.approx(est.usd * 2)

    def test_bloqueia_acima_do_teto(self, ledger):
        est = estimate_cost("opencode-go", "kimi-k3",
                             Usage(input_tokens=1_000_000, output_tokens=1_000_000))
        ledger.record(est)
        decisao = ledger.check("opencode-go", ceiling_usd=0.01)
        assert decisao.allowed is False
        assert decisao.reason

    def test_permite_dentro_do_teto(self, ledger):
        decisao = ledger.check("opencode-go", ceiling_usd=100.0)
        assert decisao.allowed is True

    def test_superficie_gratuita_nao_bloqueia(self, ledger):
        decisao = ledger.check("local-ollama", ceiling_usd=0.0)
        assert decisao.allowed is True

    def test_tarifa_desconhecida_bloqueia(self, ledger):
        """Não se presume barato o que não se sabe precificar."""
        est = estimate_cost("opencode-go", "sem-tarifa",
                             Usage(input_tokens=1000, output_tokens=1000))
        decisao = ledger.check("opencode-go", ceiling_usd=10.0, pending=est)
        assert decisao.allowed is False
        assert "tarifa" in decisao.reason.lower() or "desconhec" in decisao.reason.lower()

    def test_ledger_persiste_entre_instancias(self, tmp_path):
        from integrations.cost_governance import BudgetLedger

        caminho = tmp_path / "ledger.jsonl"
        primeiro = BudgetLedger(path=caminho)
        est = estimate_cost("opencode-go", "mimo-v2.6-flash",
                             Usage(input_tokens=1000, output_tokens=1000))
        primeiro.record(est)
        segundo = BudgetLedger(path=caminho)
        assert segundo.usage_usd("opencode-go") == pytest.approx(est.usd)

    def test_ledger_nao_registra_custo_desconhecido_como_zero(self, ledger):
        est = estimate_cost("opencode-go", "sem-tarifa",
                             Usage(input_tokens=1000, output_tokens=1000))
        ledger.record(est)
        assert ledger.usage_usd("opencode-go") == 0.0
        assert ledger.unknown_count("opencode-go") == 1


# ── CA8 — integração com a configuração do OpenCode ──────────────────────────

class TestIntegracaoConfig:
    def test_opencode_json_expoe_custo_por_modelo(self):
        from integrations.opencode_cli import build_config

        config = build_config()
        modelos = config["provider"]["opencode-go"]["models"]
        assert "mimo-v2.6-flash" in modelos, "modelo econômico ausente do catálogo Go"
        custo = modelos["mimo-v2.6-flash"].get("cost")
        assert custo and custo["input"] == pytest.approx(0.14)
        assert custo["output"] == pytest.approx(0.28)

    def test_modelos_free_publicados_trazem_custo_zero(self):
        from integrations.opencode_cli import build_config

        config = build_config()
        modelos = config["provider"]["opencode-zen"]["models"]
        assert "mimo-v2.6-flash-free" in modelos, "modelo free ausente do catálogo Zen"
        assert modelos["mimo-v2.6-flash-free"]["cost"]["input"] == 0

    def test_agentes_recebem_cadeia_de_fallback(self):
        from integrations.opencode_cli import build_config

        config = build_config()
        agentes = config["agent"]
        com_cadeia = [
            a for a in agentes.values()
            if a.get("options", {}).get("model_fallbacks")
        ]
        assert len(com_cadeia) == len(agentes), (
            f"apenas {len(com_cadeia)}/{len(agentes)} agentes têm cadeia de fallback"
        )

    def test_modelo_padrao_global_nao_mudou(self):
        """A política não substitui o modelo padrão global em silêncio."""
        from integrations.opencode_cli import build_config

        config = build_config()
        assert config["model"] == "ollama-local/llama3.2"

    def test_agente_com_modelo_declarado_preserva_o_modelo(self):
        from integrations.opencode_cli import build_config

        config = build_config()
        assert config["agent"]["kdp-orchestrator-phd"]["model"] == "opencode/deepseek-v4-pro"

    def test_nenhum_id_pendurado_entre_cadeia_e_catalogo(self):
        """Toda cadeia aponta para um modelo realmente declarado no config."""
        from integrations.opencode_cli import build_config

        config = build_config()
        disponiveis = {
            provider: set(provider_cfg.get("models", {}))
            for provider, provider_cfg in config["provider"].items()
        }
        for nivel in COMPLEXITIES:
            for ref in agent_chain(nivel):
                provider, modelo = ref.split("/", 1)
                assert modelo in disponiveis.get(provider, set()), (
                    f"cadeia {nivel} aponta para '{ref}', ausente do catálogo de '{provider}'"
                )


# ── CA9 — superfície de comando ──────────────────────────────────────────────

class TestComandoCustos:
    def test_comando_esta_registrado_no_opencode(self):
        from integrations.opencode_cli import build_config

        comandos = build_config()["command"]
        assert "custos" in comandos
        assert "core_command" in comandos["custos"]["template"]

    def test_comando_executa_e_devolve_superficies(self):
        from integrations.opencode_commands import execute_request

        envelope = execute_request({"command": "custos"})
        assert envelope["success"] is True
        superficies = envelope["result"]["surfaces"]
        assert superficies
        assert any(s["kind"] == "local_compute" for s in superficies)
        assert any(s["kind"] == "subscription" for s in superficies)
        assert envelope["limitations"], "o comando deve declarar os seus limites"

    def test_relatorio_separa_token_economy_de_dinheiro(self):
        from integrations.cost_governance import report

        relatorio = report()
        assert "token economy" in relatorio["separation_note"].lower()

    def test_nvidia_e_declarada_mas_nao_habilitada(self):
        """A governança não habilita provider sem chave do operador."""
        from integrations.cost_governance import suggested_provider_blocks
        from integrations.opencode_cli import build_config

        config = build_config()
        assert "nvidia" not in config["provider"]
        blocos = suggested_provider_blocks()
        assert "nvidia-nim" in blocos
        assert "NVIDIA_API_KEY" in blocos["nvidia-nim"]["options"]["apiKey"]

    def test_cli_custos_devolve_json_purto(self):
        """O stdout do comando é JSON: nada de aviso no mesmo fluxo."""
        import subprocess
        import sys

        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processo = subprocess.run(
            [sys.executable, "-m", "marceloclaro.cli", "custos"],
            cwd=raiz, capture_output=True, text=True, timeout=300,
        )
        assert processo.returncode == 0, processo.stderr[-800:]
        dados = json.loads(processo.stdout)
        assert dados["surfaces"]
        assert dados["chains"]["media"]

