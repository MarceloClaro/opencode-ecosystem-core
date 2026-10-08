# -*- coding: utf-8 -*-
"""PolymathLabsScanner — cobertura, licença e reprodutibilidade (SPEC-935-R712/R713).

Hermético: sem rede/subprocesso/LLM. Todo resultado carrega
`candidato_a_inspecao + exige_validacao_externa`.
"""
from __future__ import annotations

from typing import Any, Dict, List

TIPOS_EXIGIDOS = ["dedutivo", "indutivo", "abdutivo", "causal", "bayesiano", "contrafactual", "sintese"]


class PolymathLabsScanner:
    """Audita configuração polímata declarada (não executa terceiros)."""

    def varrer(self, config: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(config, dict):
            raise ValueError("config deve ser objeto.")
        tipos = [str(t).lower() for t in config.get("tipos_cobertos", []) if str(t).strip()]
        cobertos = sorted({t for t in tipos if t in TIPOS_EXIGIDOS})
        faltantes = [t for t in TIPOS_EXIGIDOS if t not in cobertos]
        licencas = list(config.get("licencas", []))
        undeclared = sum(1 for l in licencas if str(l).lower() != "ok")
        tem_manifesto = bool(config.get("tem_manifesto"))
        tem_head = bool(config.get("tem_head"))
        tem_hash = bool(config.get("tem_hash"))
        pin_fresco = config.get("pin_fresco", None)
        riscos: List[str] = []
        recomendacoes: List[str] = []
        if pin_fresco is False:
            riscos.append("Pinagem desatualizada: revalidar 90d via R713 antes de federar.")
            recomendacoes.append("Executar revalidar_todos + emitir_pins com fetcher vivo e consentimento.")
        if faltantes:
            riscos.append(f"Cobertura incompleta: faltam {', '.join(faltantes)}.")
            recomendacoes.append(f"Acrescentar labs R711 para: {', '.join(faltantes)}.")
        if undeclared:
            riscos.append(f"Licenças a confirmar: {undeclared} entrada(s) license_undeclared; federação bloqueada.")
            recomendacoes.append("Confirmar licença viva antes de federar (R711 §3).")
        if not (tem_manifesto and tem_head and tem_hash):
            riscos.append("Reprodutibilidade incompleta: exigir manifesto + HEAD + hash (R711 AC3/AC4).")
            recomendacoes.append("Emitir labs_manifest.json e auditar clones via MCP auditar_clones.")
        if len(cobertos) >= 7 and undeclared == 0 and tem_manifesto and tem_head and tem_hash:
            status = "pronto"
        elif undeclared > 0 and not (tem_manifesto and tem_head and tem_hash):
            status = "bloqueado"
        elif not cobertos:
            status = "bloqueado"
        else:
            status = "parcial"
        if not recomendacoes:
            recomendacoes.append("Configuração íntegra; manter pinagem viva e revalidação de 90 dias.")
        return {
            "cobertura_tipos": {"exigidos": list(TIPOS_EXIGIDOS), "cobertos": len(cobertos), "tipos": cobertos, "faltantes": faltantes},
            "licencas": {"total": len(licencas), "undeclared": undeclared},
            "reprodutibilidade": {"manifesto": tem_manifesto, "head": tem_head, "hash": tem_hash, "pin_fresco": pin_fresco},
            "riscos": riscos,
            "recomendacoes": recomendacoes,
            "status": status,
            "rotulo": "candidato_a_inspecao",
            "exige_validacao_externa": True,
        }


polymath_labs_scanner = PolymathLabsScanner()
