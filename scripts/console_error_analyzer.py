#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console Error Analyzer — Classificador automático de logs do navegador
======================================================================
Classifica cada linha de console do Chrome em:
  - extension      (extensões: eesel AI, searchitfastnow, refresh, single-player)
  - infrastructure (Cloudflare 524, WebSocket falha local)
  - informational  (THREE.js, navegação, lazy load, background)
  - unknown        (não reconhecido)

Uso:
  python3 scripts/console_error_analyzer.py caminho/erro.txt
  python3 scripts/console_error_analyzer.py -  (stdin)
"""
import os
import sys
import json
from typing import List, Dict

# ── Dicionário de extensões Chrome conhecidas ──────────────────────────

EXTENSION_PATTERNS: Dict[str, Dict] = {
    "eesel AI": {
        "ids": [],
        "files": ["content.bundle.js", "index.iife.js", "contentScript.js"],
        "keywords": ["eesel ai", "Initialized eesel", "from background",
                      "content script loaded"],
    },
    "searchitfastnow": {
        "ids": ["biaggnjibplcfekllonekbonhfgchopo"],
        "files": ["Index.bab7a582.js"],
        "keywords": [],
    },
    "refresh": {
        "ids": ["imbddededgmcgfhfpcjmijokokekbkal"],
        "files": ["refresh.js"],
        "keywords": ["WebSocket connection to 'ws://localhost:8081/'"],
    },
    "single-player": {
        "ids": [],
        "files": ["single-player.bundle.js"],
        "keywords": ["Single-player", "agent-chat feature flag"],
    },
}

INFRASTRUCTURE_PATTERNS = [
    ("cloudflare", ["status of 524", "524 ()"]),
    ("websocket", ["WebSocket connection to 'ws://"]),
]

INFORMATIONAL_PATTERNS = [
    ("three.js", ["THREE.WebGLRenderer"]),
    ("navigation", ["Navegou para"]),
    ("browser", ["[Intervention]", "Images loaded lazily",
                  "Load events are deferred"]),
    ("background", ["Background script ready"]),
    ("feature", ["Unrecognized feature", "allowfullscreen", "Allow attribute "]),
]


class ConsoleErrorAnalyzer:
    """
    Analisa linhas de console do navegador e classifica cada uma.
    """

    def classify(self, line: str) -> Dict[str, str]:
        line_lower = line.lower().strip()
        if not line_lower:
            return {"category": "unknown", "source": "unknown", "severity": "info"}

        # 0. Informacional (deve vir ANTES de extensões para capturar
        #    "Background script ready" mesmo via content.bundle.js)
        for source, keywords in INFORMATIONAL_PATTERNS:
            for kw in keywords:
                if kw.lower() in line_lower:
                    sev = "warning" if "intervention" in line_lower else "info"
                    return {"category": "informational", "source": source, "severity": sev}

        # 1. Extensões Chrome (por ID, arquivo, keyword)
        for ext_name, patterns in EXTENSION_PATTERNS.items():
            # por ID de extensão (chrome-extension://<id>/...)
            for ext_id in patterns.get("ids", []):
                if ext_id in line_lower:
                    sev = "error" if "ERR_FILE_NOT_FOUND" in line or "Failed to fetch" in line else "warning"
                    return {"category": "extension", "source": ext_name, "severity": sev}
            # por nome de arquivo
            for fname in patterns.get("files", []):
                if fname.lower() in line_lower:
                    sev = "info"
                    if "disabled" not in line_lower:
                        sev = "info"
                    return {"category": "extension", "source": ext_name, "severity": sev}
            # por keyword
            for kw in patterns.get("keywords", []):
                if kw.lower() in line_lower:
                    return {"category": "extension", "source": ext_name, "severity": "info"}

        # Stack traces com extensão no path
        if "chrome-extension://" in line_lower:
            for ext_name, patterns in EXTENSION_PATTERNS.items():
                for ext_id in patterns.get("ids", []):
                    if ext_id in line_lower:
                        return {"category": "extension", "source": ext_name, "severity": "info"}

        # 2. Infraestrutura
        for source, keywords in INFRASTRUCTURE_PATTERNS:
            for kw in keywords:
                if kw.lower() in line_lower:
                    return {"category": "infrastructure", "source": source, "severity": "warning"}

        # 3. Informacional
        for source, keywords in INFORMATIONAL_PATTERNS:
            for kw in keywords:
                if kw.lower() in line_lower:
                    sev = "warning" if "intervention" in line_lower else "info"
                    return {"category": "informational", "source": source, "severity": sev}

        # 4. Extensão genérica (hash filename) — fallback após todos os padrões
        import re as _re
        ext_hash = _re.search(r'[0-9a-f]{20,}-v?\d+\.js', line_lower)
        if ext_hash:
            return {"category": "extension", "source": "ext-desconhecida", "severity": "warning"}

        return {"category": "unknown", "source": "unknown", "severity": "info"}

    def analyze(self, lines: List[str]) -> Dict:
        results = []
        categories: Dict[str, int] = {}
        sources: Dict[str, int] = {}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            cls = self.classify(stripped)
            cat = cls["category"]
            src = cls["source"]
            categories[cat] = categories.get(cat, 0) + 1
            sources[src] = sources.get(src, 0) + 1
            results.append({
                "line": stripped,
                "category": cat,
                "source": src,
                "severity": cls["severity"],
            })

        extension_ok = categories.get("extension", 0) > 0
        infrastructure_ok = categories.get("infrastructure", 0) > 0
        real_errors = categories.get("unknown", 0)

        return {
            "total": len(results),
            "categories": dict(sorted(categories.items())),
            "sources": dict(sorted(sources.items())),
            "extension_only": extension_ok and categories.get("infrastructure", 0) == 0 and real_errors == 0,
            "has_real_errors": real_errors > 0,
            "lines": results,
        }

    def generate_report(self, analysis: Dict) -> str:
        lines_out = []
        lines_out.append("═" * 56)
        lines_out.append("═ CONSOLE ERROR ANALYZER — Relatório de Erros")
        lines_out.append(f"═ {analysis['total']} linhas analisadas")
        lines_out.append("═" * 56)
        lines_out.append("")

        if analysis["categories"]:
            lines_out.append("── Categorias ──────────────────────────────────")
            for cat, count in analysis["categories"].items():
                label = {
                    "extension": "Extensões Chrome",
                    "infrastructure": "Infraestrutura",
                    "informational": "Informacional",
                    "unknown": "Desconhecido",
                }.get(cat, cat)
                lines_out.append(f"  {label}: {count}")
            lines_out.append("")

            lines_out.append("── Fontes ───────────────────────────────────────")
            for src, count in analysis["sources"].items():
                lines_out.append(f"  {src}: {count}")
            lines_out.append("")

        if analysis["extension_only"]:
            lines_out.append("═══ ZERO ERROS DE CÓDIGO DO SITE ═══")
            lines_out.append("  (apenas extensões Chrome — irrelevantes)")
        elif analysis["has_real_errors"]:
            lines_out.append("═══ ATENÇÃO: ERROS NÃO CLASSIFICADOS ENCONTRADOS ═══")
        else:
            lines_out.append("═══ ZERO ERROS DE CÓDIGO DO SITE ═══")

        lines_out.append("")
        return "\n".join(lines_out)


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-":
        data = sys.stdin.read()
    else:
        path = sys.argv[1]
        if not os.path.exists(path):
            print(f"Erro: arquivo não encontrado: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()

    lines = data.splitlines()
    analyzer = ConsoleErrorAnalyzer()
    analysis = analyzer.analyze(lines)

    if "--json" in sys.argv:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    else:
        print(analyzer.generate_report(analysis))

    if analysis["has_real_errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
