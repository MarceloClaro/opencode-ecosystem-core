# -*- coding: utf-8 -*-
"""Contrato canônico de metadados do catálogo de modelos (SPEC-935-R622).

Cada provider anuncia seu próprio schema; ``ModelRouter.list_all_models()``
concatena esses dicionários cru. Antes da R622 essa_surface expunha quatro
defeitos ao consumidor:

  A1 ``runai`` emitia ``id`` e não ``model_id``;
  A2 ``litert-lm`` emitia ``context`` e ``context_window`` conflitantes;
  A3 ``Qwen3-0.6B`` reportava ``family="google"`` herdada do alias Gemma;
  A4 26 de 46 modelos não declaravam ``free``.

Estes testes são o gate: falham no baseline e só passam com a reconciliação.
"""

from __future__ import annotations

import pytest

from integrations import litert_lm_provider, litert_lm, runai
from integrations.model_router import (
    CONTEXT_DEFAULTS,
    FREE_DEFAULTS,
    model_router,
    normalize_model_entry,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def catalogo() -> list[dict]:
    """O catálogo agregado já normalizado, materializado uma única vez."""
    return model_router.list_all_models()


@pytest.fixture(scope="module")
def catalogo_cru() -> list[dict]:
    """As fontes antes da reconciliação, montadas direto nos providers.

    ``list_all_models()`` já normaliza, então chamá-lo de novo não produziria
    material cru. O objetivo aqui é provar que a normalização é aditiva e não
    contamina os catálogos de origem.
    """
    return _raw_sources()


def _raw_sources() -> list[dict]:
    """Agrega as mesmas fontes de ``list_all_models()``, sem reconciliação."""
    from integrations.free_model_catalog import list_free_models

    raw: list[dict] = []
    for getter, kwargs in (
        (model_router._go_provider, {}),
        (model_router._zen_provider, {}),
        (model_router._lt_provider, {"local_only": True}),
        (model_router._oa_provider, {}),
        (model_router._runai_provider, {}),
    ):
        if getter is not None:
            raw.extend(getter.list_models(**kwargs))
    raw.extend(list_free_models())
    return raw


# ── CA1 / CA2 — identidade ───────────────────────────────────────────────────

class TestIdentidade:
    def test_todo_modelo_tem_identidade(self, catalogo):
        """CA1/CA2: toda entrada carrega ``model_id`` e nenhum ``id`` o contradiz."""
        assert catalogo, "catálogo vazio — a lista de modelos é o contrato"

        sem_identidade = [m for m in catalogo if not m.get("model_id")]
        assert not sem_identidade, (
            f"{len(sem_identidade)} modelos sem 'model_id' (A1): "
            f"{[m.get('name') for m in sem_identidade][:5]}"
        )

        divergentes = [
            m for m in catalogo
            if "id" in m and m["id"] != m["model_id"]
        ]
        assert not divergentes, (
            f"{len(divergentes)} modelos com 'id' divergente de 'model_id': "
            f"{[(m['id'], m['model_id']) for m in divergentes][:5]}"
        )

    def test_runai_emite_ambas_as_chaves(self):
        """CA14: o runai emite ``id`` e ``model_id`` coerentes (retrocompatível)."""
        modelos = runai.runai_provisioner.list_models()
        assert modelos, "catálogo runai vazio"

        for modelo in modelos:
            assert "id" in modelo, f"runai perdeu 'id' (regra de retrocompatibilidade)"
            assert modelo.get("model_id") == modelo["id"], (
                f"runaiincoerente: id={modelo['id']!r} "
                f"model_id={modelo.get('model_id')!r}"
            )

    def test_normalizacao_pura_com_entrada_minima(self):
        """CA13: a função é utilizável fora do router, sem dependência de estado."""
        normalizado = normalize_model_entry({"model_id": "x/y", "provider": "runai"})

        assert normalizado["model_id"] == "x/y"
        assert normalizado["free"] is True
        # Única ressalva legítima: a entrada mínima não publica contexto, então
        # o piso de política entra marcado. Nada mais é inventado.
        assert normalizado["contract_errors"] == ["context_unknown"]


# ── CA3 / CA4 / CA5 — contexto ───────────────────────────────────────────────

class TestContexto:
    def test_todo_modelo_tem_contexto_unico(self, catalogo):
        """CA3/CA4/CA5: um inteiro positivo, uma chave, nenhum conflito calado."""
        invalidos = [
            m for m in catalogo
            if not isinstance(m.get("context_window"), int)
            or m["context_window"] <= 0
        ]
        assert not invalidos, (
            f"{len(invalidos)} modelos sem 'context_window' inteiro positivo: "
            f"{[(m.get('model_id'), m.get('context_window')) for m in invalidos][:5]}"
        )

        residuais = [m for m in catalogo if "context" in m]
        assert not residuais, (
            f"{len(residuais)} modelos ainda carregam a chave duplicada 'context' "
            f"(A2): {[m.get('model_id') for m in residuais][:5]}"
        )

        silenciosos = [
            m for m in catalogo
            if "context_conflict" in m.get("contract_errors", [])
            and not m.get("context_window")
        ]
        assert not silenciosos, "conflito de contexto registrado sem resolução"

    def test_conflito_prevalece_o_campo_contractado(self):
        """CA5: quando há conflito, o campo contratado por R211 prevalece."""
        normalizado = normalize_model_entry({
            "model_id": "prov/x",
            "provider": "litert-lm",
            "context": 20_480,
            "context_window": 32_768,
        })

        assert normalizado["context_window"] == 20_480
        assert "context" not in normalizado
        assert "context_conflict" in normalizado["contract_errors"]

    def test_contexto_so_com_a_chave_legada_e_adotado(self):
        """CA3: quem só publica a chave antiga ainda é normalizado."""
        normalizado = normalize_model_entry({
            "model_id": "prov/x",
            "provider": "runai",
            "context": 8_192,
        })

        assert normalizado["context_window"] == 8_192
        assert "context" not in normalizado
        assert "context_conflict" not in normalizado["contract_errors"]

    def test_r211_politica_de_contexto_preservada(self):
        """CA9: a política 20480 do catálogo canônico NÃO foi reescrita (R211)."""
        contextos = {m["context"] for m in litert_lm_provider.MODELS.values()}
        assert contextos == {20_480}, (
            f"R211 violado — catálogo canônico publikou {sorted(contextos)}"
        )

    def test_contexto_ausente_vira_piso_declarado_e_sinalizado(self):
        """CA17: quem cala recebe o piso da política, jamais um número calado."""
        normalizado = normalize_model_entry({
            "model_id": "runai/qwen3.5-4b",
            "provider": "runai",
        })

        assert normalizado["context_window"] == CONTEXT_DEFAULTS["runai"]
        assert isinstance(normalizado["context_window"], int)
        assert "context_unknown" in normalizado["contract_errors"], (
            "contexto suprimido pela política precisa ser sinalizado ao consumidor"
        )

    def test_contexto_publicado_nao_e_marcado_como_desconhecido(self, catalogo):
        """CA17: a marcação distingue o que o provider disse do que a política supriu."""
        for modelo in catalogo:
            origem_conhece = modelo.get("provider") != "runai"
            marcada = "context_unknown" in modelo.get("contract_errors", [])
            if origem_conhece:
                assert not marcada, (
                    f"{modelo['model_id']} publishes contexto mas foi marcado "
                    f"como desconhecido"
                )


# ── CA6 / CA7 — gratuidade ───────────────────────────────────────────────────

class TestGratuidade:
    def test_todo_modelo_declara_gratuidade(self, catalogo):
        """CA6: ``free`` é sempre booleano, nunca ausente nem ``None``."""
        sem_free = [m for m in catalogo if not isinstance(m.get("free"), bool)]
        assert not sem_free, (
            f"{len(sem_free)} modelos sem 'free' booleano (A4): "
            f"{sorted({m.get('provider') for m in sem_free})}"
        )

    def test_free_desconhecido_e_sinalizado(self):
        """CA7: provider fora da política recebe default pessimista *e* o erro."""
        normalizado = normalize_model_entry({
            "model_id": "desconhecido/x",
            "provider": "provider-que-nao-existe",
        })

        assert normalizado["free"] is False
        assert "free_unknown" in normalizado["contract_errors"]

    def test_politica_explicita_para_os_provedores_conhecidos(self):
        """CA2/RF2: a política é declarada, não inferida — e é fail-closed."""
        for provider in ("litert-lm", "runai"):
            assert FREE_DEFAULTS[provider] is True, (
                f"{provider} é local/on-device e não pode custar token"
            )
        for provider in ("openai", "opencode-go", "opencode-zen"):
            assert FREE_DEFAULTS[provider] is False, (
                f"{provider} é metered; o default precisa ser pessimista"
            )


# ── CA8 / CA16 — família ─────────────────────────────────────────────────────

class TestFamilia:
    def test_familia_nao_atravessa_alias(self):
        """CA8: a família do Qwen é a do Qwen, não a do alias Gemma que o mapeia."""
        # A fachada legada indexa o catálogo pelo ID, mas não o repete dentro
        # do valor — quem injeta a identidade é `list_models()`. A reconciliação
        # é testada sobre a mesma forma que o agregador entrega.
        canônico = litert_lm_provider.MODELS["litert-community/Qwen3-0.6B"]
        mesclado = litert_lm.MODELS["litert-community/Qwen3-0.6B"]

        normalizado = normalize_model_entry({
            "model_id": "litert-community/Qwen3-0.6B", **mesclado
        })

        assert normalizado["model_id"] == "litert-community/Qwen3-0.6B"
        assert canônico["family"] == "qwen"
        assert normalizado["family"] == "qwen", (
            f"Qwen3-0.6B reporta family={normalizado['family']!r} — "
            f"atributo de identidade atravessou o alias (A3)"
        )

    def test_catalogo_canonico_litert_autossuficiente(self):
        """CA16: o catálogo canônico declara família e gratuidade sozinho."""
        for model_id, meta in litert_lm_provider.MODELS.items():
            assert meta.get("family"), f"{model_id} canônico sem 'family' declarada"
            assert isinstance(meta.get("free"), bool), (
                f"{model_id} canônico sem 'free' declarada"
            )
            # `family` não pode mais ser herdado do catálogo legado.
            assert "family" not in litert_lm.LEGACY_MODELS.get(
                "gemma-3-1B-it", {}
            ) or litert_lm_provider.MODELS[model_id]["family"] != "google" or (
                "Qwen" not in model_id
            ), f"{model_id} herdou família do alias legado"


# ── CA10 / CA11 / CA12 / CA15 — propriedades da normalização ────────────────

class TestPropriedades:
    def test_normalizacao_preserva_metadados_especificos(self):
        """CA10: a reconciliação é aditiva; nada de provider é apagado."""
        entrada = {
            "model_id": "litert-community/Qwen3-0.6B",
            "provider": "litert-lm",
            "name": "Qwen3 0.6B",
            "size_gb": 0.58,
            "backend": "cpu",
            "description": "leve para testes",
            "task_types": ["fast", "local"],
            "context": 20_480,
            "strengths": ["fast", "simple"],
            "score": 0.923,
            "source": "curadoria R499",
            "accessible": True,
        }
        esperado = set(entrada) - {"context"}

        normalizado = normalize_model_entry(entrada)

        for chave in esperado:
            assert chave in normalizado, f"normalização apagou '{chave}'"
            assert normalizado[chave] == entrada[chave], (
                f"normalização alterou o valor de '{chave}'"
            )
        assert normalizado["contract_errors"] == []

    def test_normalizacao_e_idempotente(self):
        """CA11: normalizar duas vezes não muda o resultado nem acumula erros."""
        primeira = normalize_model_entry({
            "model_id": "prov/x",
            "provider": "litert-lm",
            "context": 20_480,
            "context_window": 32_768,
            "strengths": ["b", "a"],
        })
        segunda = normalize_model_entry(primeira)

        assert segunda == primeira

    def test_normalizacao_nao_muta_entrada(self, catalogo_cru):
        """CA12: a função é pura — o dicionário de origem fica intacto."""
        entrada = {
            "model_id": "prov/x",
            "provider": "opencode-go",
            "context": 20_480,
        }
        copia = dict(entrada)

        normalize_model_entry(entrada)

        assert entrada == copia, "normalize_model_entry mutou o argumento"
        # O agregador do router também não pode contaminar a fonte.
        assert all(not m.get("contract_errors") for m in catalogo_cru), (
            "o catálogo agregado foi consumido já normalizado — a fonte "
            "do provider foi mutada"
        )

    def test_normalizacao_nao_altera_contagem(self, catalogo, catalogo_cru):
        """CA15: a mesma lista de modelos antes e depois — nenhum gains/perdas."""
        assert len(catalogo) == len(catalogo_cru), (
            f"contagem mudou na normalização: "
            f"{len(catalogo_cru)} → {len(catalogo)}"
        )
        assert [m["model_id"] for m in catalogo] == [
            m.get("model_id", m.get("id")) for m in catalogo_cru
        ]

    def test_lista_ordenada_e_deterministica(self, catalogo):
        """CA1: a ordem das fontes é estável entre chamadas."""
        assert [m["model_id"] for m in catalogo] == [
            m["model_id"] for m in model_router.list_all_models()
        ]
