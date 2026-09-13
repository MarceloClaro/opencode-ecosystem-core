# -*- coding: utf-8 -*-
"""landscape-curator — curadoria da paisagem de agentes externos (R482).

Consome o manifest curado ``landscape/manifest.json`` (20 agentes auto-contidos
da coleção 500-AI-Agents-Projects, MIT), cruza cada caso de uso com o catálogo
de agent cards do Core (agents/catalog/*.md) por afinidade lexical e produz um
relatório auditável (JSON + Markdown).

Regras:
- Nenhum código-fonte externo é importado (apenas metadados curados).
- Casos sem afinidade real entram em ``unmatched`` — nunca são inventados.
- O relatório contém a ressalva de que não constitui certificação externa.
"""

from __future__ import annotations

import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    yaml = None

DEFAULT_MANIFEST = "landscape/manifest.json"
DEFAULT_CATALOG = "agents/catalog"

# Keywords de afinidade por caso de uso externo (cruzam com name/description/tags
# dos agent cards do Core). Não são palavras mágicas: apenas heurística lexical
# auditável.
CASE_KEYWORDS: Dict[str, List[str]] = {
    "01-web-research-agent": ["web", "research", "search", "researcher", "internet"],
    "02-code-review-agent": ["code", "review", "reviewer", "revisão", "quality", "audit"],
    "03-pdf-qa-agent": ["pdf", "document", "qa", "question", "knowledge", "query"],
    "04-sql-query-agent": ["sql", "database", "query", "data"],
    "05-email-drafting-agent": ["email", "communication", "writing", "writer", "copy"],
    "06-news-summarizer-agent": ["news", "summar", "media", "summary", "content"],
    "07-github-issue-triager": ["github", "issue", "triage", "git", "task", "manager"],
    "08-data-analysis-agent": ["data", "analysis", "analytics", "pandas", "statistic"],
    "09-resume-parser-agent": ["resume", "curriculum", "cv", "career", "hr", "recrut"],
    "10-meeting-notes-agent": ["meeting", "notes", "ata", "productivity", "document"],
    "11-stock-research-agent": ["stock", "finance", "market", "financial", "research"],
    "12-travel-planner-agent": ["travel", "trip", "itinerary", "planner", "hospitality"],
    "13-customer-support-agent": ["support", "customer", "service", "chat", "assistant"],
    "14-social-media-agent": ["social", "media", "marketing", "content", "copywriter"],
    "15-unit-test-generator": ["test", "unit", "testing", "code", "quality"],
    "16-documentation-writer": ["documentation", "docs", "writer", "technical", "write"],
    "17-recipe-agent": ["recipe", "food", "cooking", "content", "writer"],
    "18-job-application-agent": ["job", "application", "career", "resume", "hr", "recrut"],
    "19-competitive-analysis-agent": ["competitive", "analysis", "market", "business", "strategy"],
    "20-multi-agent-debate": ["multi", "agent", "debate", "collaboration", "orchestr"],
}

_BANNED = ("superhuman", "verificado", "qualis a1", "superação")


class LandscapeCurator:
    """Curador da paisagem de agentes externos vs catálogo do Core."""

    def __init__(self, repo_root: str | None = None,
                 manifest_path: str | None = None,
                 catalog_dir: str | None = None) -> None:
        self.root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
        self.manifest_path = pathlib.Path(manifest_path or (self.root / DEFAULT_MANIFEST))
        self.catalog_dir = pathlib.Path(catalog_dir or (self.root / DEFAULT_CATALOG))
        self.manifest = self._load_manifest()
        self.agent_cards = self._load_catalog()

    # ---------- cargas ----------
    def _load_manifest(self) -> dict:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _load_catalog(self) -> List[Dict[str, Any]]:
        cards = []
        for md in sorted(self.catalog_dir.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            data = self._parse_frontmatter(text)
            if data:
                cards.append({
                    "name": str(data.get("name", md.stem)),
                    "description": str(data.get("description", "")),
                    "tags": " ".join(
                        str(t) for t in (data.get("tags", []) or [])
                    ),
                    "category": str(data.get("category", "")),
                })
        return cards

    @staticmethod
    def _parse_frontmatter(text: str) -> dict:
        start = text.find("---")
        if start < 0:
            return {}
        end = text.find("\n---", start + 3)
        if end < 0:
            return {}
        block = text[start + 3:end]
        if yaml is not None:
            try:
                return yaml.safe_load(block) or {}
            except Exception:
                return {}
        # fallback mínimo sem PyYAML
        data: Dict[str, Any] = {}
        for line in block.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip("'\"")
                if key in {"tags", "examples", "skills"}:
                    data[key] = re.findall(r"[\w-]+", value)
                else:
                    data[key] = value
        return data

    # ---------- cruzamento ----------
    def _score_case(self, case_id: str, card: dict) -> int:
        keywords = CASE_KEYWORDS.get(case_id, [])
        name = card["name"].lower()
        tags = card["tags"].lower()
        description = card["description"].lower()
        score = 0
        for kw in keywords:
            if kw in name:
                score += 2
            if kw in tags:
                score += 2
            if kw in description:
                score += 1
        return score

    def match_case(self, case: dict) -> List[Dict[str, Any]]:
        scored = [
            {"core_agent": c["name"], "score": s}
            for c in self.agent_cards
            if (s := self._score_case(case["id"], c)) > 0
        ]
        scored.sort(key=lambda x: (-x["score"], x["core_agent"]))
        return scored[:3]

    def build_report(self) -> Dict[str, Any]:
        cases: List[Dict[str, Any]] = []
        unmatched: List[Dict[str, Any]] = []
        matched = 0
        for agent in self.manifest["agents"]:
            suggestions = self.match_case(agent)
            entry = {
                "case_id": agent["id"],
                "title": agent["title"],
                "industry": agent["industry"],
                "framework": agent["framework"],
                "license": agent["license"],
                "suggestions": suggestions,
            }
            cases.append(entry)
            if suggestions:
                matched += 1
            else:
                unmatched.append({"case_id": agent["id"], "title": agent["title"]})
        report = {
            "report": "landscape-curator",
            "collection": self.manifest["collection"],
            "source_repo": self.manifest["source_repo"],
            "upstream": self.manifest["upstream"],
            "license": self.manifest["license"],
            "counters": {
                "external_cases": len(self.manifest["agents"]),
                "catalog_cards": len(self.agent_cards),
                "matched": matched,
                "unmatched": len(unmatched),
            },
            "cases": cases,
            "unmatched": unmatched,
            "disclaimer": "Relatório interno de curadoria; não constitui certificação externa nem promessa de integração.",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        return report

    # ---------- render ----------
    def render_markdown(self, report: dict) -> str:
        lines = [
            "# Paisagem de agentes — 500-AI-Agents-Projects (R482)",
            "",
            f"Coleção: **{report['collection']}** ({report['license']})",
            f"Fonte: {report['source_repo']} (upstream: {report['upstream']})",
            "",
            "| Métrica | Valor |",
            "|---|---|",
            f"| Casos externos curados | {report['counters']['external_cases']} |",
            f"| Agent cards do catálogo Core | {report['counters']['catalog_cards']} |",
            f"| Casos com sugestão core | {report['counters']['matched']} |",
            f"| Casos sem afinidade declarada | {report['counters']['unmatched']} |",
            "",
            "## Roteamentos sugeridos (top 3 afins)",
            "",
            "| Caso | Indústria | Framework | Afinidade Core |",
            "|---|---|---|---|",
        ]
        for case in report["cases"]:
            sugg = ", ".join(
                f"{s['core_agent']} ({s['score']})" for s in case["suggestions"]
            ) or "—"
            lines.append(
                f"| {case['case_id']} — {case['title']} | {case['industry']} | "
                f"{case['framework']} | {sugg} |"
            )
        lines.append("")
        if report["unmatched"]:
            lines.append("## Sem afinidade declarada (não inventados)")
            lines.append("")
            lines.extend(
                f"- {u['case_id']} — {u['title']}" for u in report["unmatched"]
            )
            lines.append("")
        lines.append(f"> {report['disclaimer']}")
        lines.append("")
        lines.append(f"_Gerado em {report['timestamp_utc']} (sem rede, sem código de terceiros)._")
        return "\n".join(lines) + "\n"

    def write_report(self, out_dir: str | None = None) -> pathlib.Path:
        out = pathlib.Path(out_dir or self.root)
        out.mkdir(parents=True, exist_ok=True)
        report = self.build_report()
        md_path = out / "LANDSCAPE_REPORT.md"
        md_path.write_text(self.render_markdown(report), encoding="utf-8")
        return md_path