# -*- coding: utf-8 -*-
"""
Metacognition — ingere eventos de sessão e Agent Notes do dsh no MetaBus.

Converte artefatos do dsh (session events JSON-RPC e .agents/notes/*.md) em
reflexões e tópicos semânticos do Global Workspace, preservando proveniência.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DSH_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "deepseek-harness",
)
DEFAULT_MONOREPO = os.path.join(DEFAULT_DSH_ROOT, "DEEPSEEK-HARNESS")


class DSHMetacognitionIngestor:
    """Ingestor de metacognição do dsh no MetaBus do Core."""

    def __init__(self, dsh_root: str | None = None, metabus: Any | None = None):
        self.dsh_root = os.path.abspath(dsh_root or DEFAULT_DSH_ROOT)
        self.monorepo = os.path.join(self.dsh_root, "DEEPSEEK-HARNESS")
        if metabus is not None:
            self.metabus = metabus
        else:
            from mci.metabus import metabus as _global_metabus

            self.metabus = _global_metabus

    # ------------------------------------------------------------------
    def ingest_session_events(
        self,
        events: List[Dict[str, Any]],
        task_id: str = "dsh-task",
    ) -> Dict[str, Any]:
        """Converte eventos do dsh em eventos de subsistema + reflexões.

        Cada evento com method == "session.event" é publicado como
        deepseek_harness/dsh.<event.type>. Ao final, uma reflexão síntese é
        registrada no Global Workspace.
        """
        if not isinstance(events, list):
            events = []

        session_events = [e for e in events if isinstance(e, dict) and e.get("method") == "session.event"]
        seen_types: List[str] = []

        for event in session_events:
            payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
            inner = payload.get("event", {}) if isinstance(payload.get("event"), dict) else {}
            ev_type = inner.get("type") or payload.get("type") or "session.event"
            if isinstance(ev_type, str):
                seen_types.append(ev_type)
            # Publica no subsistema deepseek_harness — auditável e assinável
            try:
                self.metabus.publish_subsystem_event(
                    "deepseek_harness",
                    f"dsh.{ev_type}",
                    {"task_id": task_id, "event": inner or payload, "raw": event},
                    source_agent="dsh-ingestor",
                )
            except Exception:
                pass

        # Reflexão síntese (padrão Reflexion) — sempre ao menos 1
        types_str = ", ".join(sorted(set(seen_types))) if seen_types else "sem tipo"
        score = 0.9 if any("completed" in t or "success" in t for t in seen_types) else (0.7 if seen_types else 0.5)
        reflection = (
            f"dsh sessão {task_id}: {len(session_events)} evento(s) de sessão "
            f"ingeridos ({types_str}). Proveniência: DEEPSEEK-HARNESS/python SDK."
        )
        try:
            self.metabus.memory.add_reflection(
                agent_id="deepseek-harness",
                task_context=f"sessão dsh {task_id}",
                reflection=reflection,
                score=score,
            )
        except Exception:
            pass

        return {
            "events_seen": len(session_events),
            "events_total": len(events),
            "types": sorted(set(seen_types)),
            "reflections_added": 1,
            "task_id": task_id,
        }

    # ------------------------------------------------------------------
    def ingest_agent_notes(self, limit: int = 20) -> Dict[str, Any]:
        """Varre .agents/notes do dsh e registra lições no MetaBus.

        O repositório dsh mantém Agent Notes implementadas em
        DEEPSEEK-HARNESS/.agents/notes/implemented/**/*.md — essas são a
        metacognição nativa do sistema. Cada nota vira uma lição com proveniência.
        """
        notes_root = Path(self.monorepo) / ".agents" / "notes"
        # Preferência: implemented; fallback: qualquer subpasta
        search_roots: List[Path] = []
        if (notes_root / "implemented").is_dir():
            search_roots.append(notes_root / "implemented")
        if not search_roots and notes_root.is_dir():
            search_roots.append(notes_root)
        elif notes_root.is_dir():
            # adiciona fallback mesmo quando implemented existe, se limit grande
            search_roots.append(notes_root)

        md_files: List[Path] = []
        for root in search_roots:
            for p in sorted(root.rglob("*.md")):
                # ignora índices/README genéricos quando há conteúdo real
                if p.name.lower() in ("readme.md", "index.md") and len(md_files) > 5:
                    continue
                # ignora arquivos ocultos
                if any(part.startswith(".") for part in p.parts):
                    continue
                md_files.append(p)
                if len(md_files) >= max(limit * 3, limit):
                    break
            if len(md_files) >= limit:
                break

        md_files = sorted(set(md_files))[:limit] if limit else sorted(set(md_files))
        # Fallback: se ainda vazio mas o repo existe, tenta busca direta por .md em .agents
        if not md_files:
            agents_dir = Path(self.monorepo) / ".agents"
            if agents_dir.is_dir():
                for p in sorted(agents_dir.rglob("*.md")):
                    if p.is_file():
                        md_files.append(p)
                        if len(md_files) >= limit:
                            break

        topics_registered = 0
        for path in md_files:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            title = self._extract_title(text, path)
            rel = str(path.relative_to(Path(self.monorepo))) if str(path).startswith(self.monorepo) else path.name
            lesson = f"[{rel}] {title}"
            try:
                self.metabus.memory.upsert_semantic_topic(
                    "deepseek_harness.agent_notes",
                    lesson=lesson,
                    metadata={
                        "provenance": "DEEPSEEK-HARNESS/.agents/notes",
                        "last_note": rel,
                        "notes_dir": str(notes_root),
                    },
                )
                topics_registered = 1  # tópico único consolidado
            except Exception:
                continue

        # Se houve notas mas nenhuma lição registrada (erro de MetaBus), ainda reporta
        return {
            "notes_scanned": len(md_files),
            "topics_registered": topics_registered if md_files else 0,
            "sample_paths": [str(p.relative_to(Path(self.monorepo))) if str(p).startswith(self.monorepo) else str(p) for p in md_files[:3]],
        }

    @staticmethod
    def _extract_title(text: str, path: Path) -> str:
        for line in text.splitlines()[:20]:
            s = line.strip()
            if s.startswith("# "):
                t = s[2:].strip()
                if t:
                    return t[:180]
            if s.startswith("title:") or s.startswith("Title:"):
                t = s.split(":", 1)[1].strip().strip('"').strip("'")
                if t:
                    return t[:180]
        # fallback: primeira linha não vazia
        for line in text.splitlines():
            s = line.strip()
            if s and not s.startswith("<!--") and not s.startswith("---"):
                return s[:180]
        return path.stem.replace("-", " ").replace("_", " ")[:180]
