# -*- coding: utf-8 -*-
"""
ReversaUniversalEngine — análise filesystem universal (SPEC-935-R437)

Analisa qualquer path (artigo, repo, código, script) e gera inventory, modules,
dependencies, data_model, gaps e recommendations sem dependências externas.
"""

from __future__ import annotations

import ast
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ── Helpers ────────────────────────────────────────────────────────────

def _read_text(path: Path, limit: int = 200_000) -> str:
    try:
        if path.stat().st_size > limit:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read(limit)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def _normalize(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


# ── Engine ─────────────────────────────────────────────────────────────

class ReversaUniversalEngine:
    """Engine universal de engenharia reversa (stdlib puro)."""

    # Frameworks detectáveis via dependencies
    FRAMEWORK_KEYWORDS = {
        "django", "flask", "fastapi", "streamlit", "gradio", "cordis", "cosmokit",
        "react", "vue", "angular", "next", "express", "nest", "cordiverse",
        "sqlalchemy", "alembic", "prisma", "typeorm",
    }
    INTEGRATION_KEYWORDS = {
        "postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis", "kafka",
        "rabbitmq", "celery", "elasticsearch", "opensearch", "qdrant", "weaviate",
        "stripe", "openai", "anthropic", "deepseek", "ollama", "litert",
    }
    SECRET_PAT = re.compile(r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE)
    TODO_PAT = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")
    LONG_LINE_PAT = re.compile(r"^.{160,}$", re.MULTILINE)

    def __init__(self):
        pass

    # ── Inventory ───────────────────────────────────────────────────
    def inventory(self, path: str | Path) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {"error": f"path não existe: {path}", "total_files": 0}
        files: List[Path] = []
        if p.is_file():
            files = [p]
            root = p.parent
        else:
            root = p
            for dirpath, _, filenames in os.walk(root):
                # ignora .git, __pycache__, .venv, node_modules, .reversa
                if any(seg in dirpath for seg in ("/.git/", "/__pycache__/", "/.venv/", "/node_modules/", "/.reversa/")):
                    continue
                for fn in filenames:
                    if fn.startswith(".") and fn not in (".env.example",):
                        continue
                    files.append(Path(dirpath) / fn)
                    if len(files) > 5000:
                        break
                if len(files) > 5000:
                    break

        total_files = len(files)
        ext_counts: Dict[str, int] = {}
        loc_by_ext: Dict[str, int] = {}
        languages: Set[str] = set()
        total_loc = 0

        for f in files:
            ext = f.suffix.lower().lstrip(".") or "noext"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            # linguagens
            if ext in ("py",):
                languages.add("python")
            elif ext in ("ts", "tsx"):
                languages.add("typescript")
            elif ext in ("js", "jsx"):
                languages.add("javascript")
            elif ext in ("md", "markdown"):
                languages.add("markdown")
            elif ext in ("json", "yaml", "yml", "toml"):
                languages.add("config")
            elif ext in ("sql",):
                languages.add("sql")
            elif ext in ("rs",):
                languages.add("rust")
            elif ext in ("go",):
                languages.add("go")
            # LOC aproximado (linhas não vazias)
            try:
                if f.is_file() and f.stat().st_size < 1_000_000 and ext in ("py", "ts", "tsx", "js", "jsx", "md", "rs", "go", "sql", "json", "yaml", "yml", "toml", "txt"):
                    txt = _read_text(f, limit=500_000)
                    loc = len([l for l in txt.splitlines() if l.strip()])
                    loc_by_ext[ext] = loc_by_ext.get(ext, 0) + loc
                    total_loc += loc
            except Exception:
                pass

        # Frameworks e integrações via dependencies e conteúdo
        frameworks: Set[str] = set()
        integrations: Set[str] = set()
        deps = self.dependencies(str(root) if p.is_dir() else str(p.parent))
        for dep in deps.get("all", []):
            name = _normalize(dep.get("name", ""))
            for kw in self.FRAMEWORK_KEYWORDS:
                if kw in name:
                    frameworks.add(kw)
            for kw in self.INTEGRATION_KEYWORDS:
                if kw in name:
                    integrations.add(kw)
        # Também varre conteúdo de package.json/requirements para keywords restantes
        for f in files[:200]:
            if f.name in ("package.json", "requirements.txt", "pyproject.toml", "Cargo.toml"):
                txt = _normalize(_read_text(f))
                for kw in self.FRAMEWORK_KEYWORDS:
                    if kw in txt:
                        frameworks.add(kw)
                for kw in self.INTEGRATION_KEYWORDS:
                    if kw in txt:
                        integrations.add(kw)

        entry_points: List[str] = []
        for cand in ("main.py", "app.py", "index.ts", "index.js", "src/main.py", "package.json", "pyproject.toml"):
            if (root / cand).exists():
                entry_points.append(cand)

        return {
            "target": str(p),
            "root": str(root),
            "total_files": total_files,
            "total_loc": total_loc,
            "ext_counts": ext_counts,
            "loc_by_ext": loc_by_ext,
            "languages": sorted(languages),
            "frameworks": sorted(frameworks),
            "integrations": sorted(integrations),
            "entry_points": entry_points,
            "metrics": {"total_files": total_files, "total_loc": total_loc},
        }

    # ── Modules ─────────────────────────────────────────────────────
    def modules(self, path: str | Path) -> List[Dict[str, Any]]:
        p = Path(path)
        if not p.exists():
            return []
        root = p if p.is_dir() else p.parent
        files: List[Path] = []
        if p.is_file():
            files = [p]
        else:
            for dirpath, _, filenames in os.walk(root):
                if any(seg in dirpath for seg in ("/.git/", "/__pycache__/", "/.venv/", "/node_modules/")):
                    continue
                for fn in filenames:
                    if fn.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".sql")):
                        files.append(Path(dirpath) / fn)
                    if len(files) > 2000:
                        break
                if len(files) > 2000:
                    break

        # Agrupa por diretório de primeiro nível ou pacote
        grouped: Dict[str, List[Path]] = {}
        for f in files:
            try:
                rel = f.relative_to(root)
            except ValueError:
                rel = Path(f.name)
            top = str(rel.parts[0]) if len(rel.parts) > 1 else "."
            # Para .py, usa pacote (diretório contendo __init__.py) como módulo
            if f.suffix == ".py":
                # sobe até achar __init__.py
                pkg = f.parent
                while pkg != root and not (pkg / "__init__.py").exists() and pkg.parent != pkg:
                    # mantém top como fallback
                    break
                # usa top como chave principal
            grouped.setdefault(top, []).append(f)

        modules: List[Dict[str, Any]] = []
        for mod_name, mod_files in sorted(grouped.items()):
            classes: List[str] = []
            functions: List[str] = []
            headings: List[str] = []
            for f in mod_files[:50]:
                if f.suffix == ".py":
                    txt = _read_text(f)
                    try:
                        tree = ast.parse(txt)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                classes.append(node.name)
                            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                                functions.append(node.name)
                    except Exception:
                        # fallback regex
                        classes.extend(re.findall(r"^\s*class\s+(\w+)", txt, re.MULTILINE))
                        functions.extend(re.findall(r"^\s*def\s+(\w+)\s*\(", txt, re.MULTILINE))
                elif f.suffix == ".md":
                    txt = _read_text(f)
                    headings.extend(re.findall(r"^#+\s+(.+)", txt, re.MULTILINE)[:5])
            modules.append({
                "name": mod_name,
                "files": len(mod_files),
                "classes": sorted(set(classes))[:20],
                "functions": sorted(set(functions))[:20],
                "headings": headings[:5],
                "sample_files": [str(f.relative_to(root)) if f.is_relative_to(root) else f.name for f in mod_files[:3]],
            })
        return modules

    # ── Dependencies ────────────────────────────────────────────────
    def dependencies(self, path: str | Path) -> Dict[str, Any]:
        p = Path(path)
        root = p if p.is_dir() else p.parent
        all_deps: List[Dict[str, str]] = []

        # requirements.txt
        for req_file in list(root.glob("requirements*.txt")) + list(root.glob("**/requirements*.txt")):
            if req_file.is_file():
                txt = _read_text(req_file)
                for line in txt.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("-"):
                        continue
                    # nome antes de ==, >=, ~=, etc.
                    m = re.match(r"([A-Za-z0-9_.\-]+)", line)
                    if m:
                        name = m.group(1)
                        version = line[len(name):].strip()
                        all_deps.append({"name": name, "version": version or "", "source_file": str(req_file.relative_to(root) if req_file.is_relative_to(root) else req_file)})

        # package.json
        for pkg_file in list(root.glob("package.json")) + list(root.glob("**/package.json")):
            if pkg_file.is_file() and "node_modules" not in str(pkg_file):
                try:
                    data = json.loads(_read_text(pkg_file))
                    for section in ("dependencies", "devDependencies", "peerDependencies"):
                        deps = data.get(section, {})
                        if isinstance(deps, dict):
                            for name, ver in deps.items():
                                all_deps.append({"name": name, "version": str(ver), "source_file": str(pkg_file.relative_to(root) if pkg_file.is_relative_to(root) else pkg_file)})
                except Exception:
                    pass
                break  # só raiz para evitar node_modules explosão

        # pyproject.toml (G3 — R438: tomllib com fallback tomli)
        for toml_file in list(root.glob("pyproject.toml")) + list(root.glob("**/pyproject.toml")):
            if toml_file.is_file():
                txt = _read_text(toml_file)
                # tenta tomllib (3.11+) com fallback tomli (G3)
                try:
                    try:
                        import tomllib
                    except ImportError:
                        import tomli as tomllib  # type: ignore
                    data = tomllib.loads(txt)
                    # PEP 621 [project.dependencies]
                    proj = data.get("project", {})
                    for dep in proj.get("dependencies", []):
                        if isinstance(dep, str):
                            m = re.match(r"([A-Za-z0-9_.\-]+)", dep)
                            if m:
                                all_deps.append({"name": m.group(1), "version": dep[len(m.group(1)):].strip(), "source_file": str(toml_file.relative_to(root) if toml_file.is_relative_to(root) else toml_file)})
                    # poetry
                    poetry = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                    for name, ver in poetry.items():
                        if name == "python":
                            continue
                        all_deps.append({"name": name, "version": str(ver), "source_file": str(toml_file.relative_to(root) if toml_file.is_relative_to(root) else toml_file)})
                except Exception:
                    # fallback regex para linhas tipo 'fastapi = "^0.100"'
                    for line in txt.splitlines():
                        line = line.strip()
                        if "=" in line and not line.startswith("[") and not line.startswith("#"):
                            # heurística simples
                            pass
                break

        # dedup por name lower
        seen: Dict[str, Dict[str, str]] = {}
        for d in all_deps:
            key = d["name"].lower()
            if key not in seen:
                seen[key] = d
        deduped = sorted(seen.values(), key=lambda x: x["name"].lower())

        return {"all": deduped, "count": len(deduped), "by_file": {}}

    # ── Data Model ──────────────────────────────────────────────────
    def data_model(self, path: str | Path) -> List[Dict[str, Any]]:
        p = Path(path)
        root = p if p.is_dir() else p.parent
        entities: List[Dict[str, Any]] = []
        # Busca models.py, schema*, *.sql, data-dictionary
        candidates: List[Path] = []
        for pattern in ("**/models.py", "**/schema*.py", "**/schemas/*.py", "**/*.sql", "**/data-dictionary*"):
            try:
                candidates.extend(list(root.glob(pattern))[:10])
            except Exception:
                pass
        for f in candidates[:20]:
            if not f.is_file() or "node_modules" in str(f) or ".venv" in str(f):
                continue
            txt = _read_text(f)
            if f.suffix == ".py":
                try:
                    tree = ast.parse(txt)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # heurística: classe com Base/Model no nome ou com atributos
                            fields = [n.target.id for n in node.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
                            # fallback para Assign
                            if not fields:
                                fields = [n.targets[0].id for n in node.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)][:10]
                            entities.append({"entity": node.name, "fields": fields[:10], "source": str(f.relative_to(root) if f.is_relative_to(root) else f)})
                except Exception:
                    pass
            elif f.suffix == ".sql":
                tables = re.findall(r"CREATE\s+TABLE\s+(\w+)", txt, re.IGNORECASE)
                for t in tables:
                    entities.append({"entity": t, "fields": [], "source": str(f.relative_to(root) if f.is_relative_to(root) else f)})
            if len(entities) >= 20:
                break
        return entities

    # ── Gaps ────────────────────────────────────────────────────────
    def gaps(self, path: str | Path, inventory: Optional[Dict[str, Any]] = None, modules: Optional[List[Dict[str, Any]]] = None, dependencies: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = Path(path)
        root = p if p.is_dir() else p.parent
        inv = inventory or self.inventory(path)
        mods = modules or self.modules(path)
        deps = dependencies or self.dependencies(path)

        # Coleta rápida de conteúdo para TODO/secrets
        todo_count = 0
        secret_count = 0
        long_files: List[str] = []
        has_readme = False
        has_tests = False
        test_files: List[str] = []

        files_to_scan: List[Path] = []
        if p.is_dir():
            for dirpath, _, filenames in os.walk(root):
                if any(seg in dirpath for seg in ("/.git/", "/__pycache__/", "/.venv/", "/node_modules/")):
                    continue
                for fn in filenames:
                    fp = Path(dirpath) / fn
                    if fn.lower() in ("readme.md", "readme.txt"):
                        has_readme = True
                    if fn.startswith("test_") or fn.endswith("_test.py") or "/tests/" in str(fp):
                        has_tests = True
                        test_files.append(str(fp.relative_to(root) if fp.is_relative_to(root) else fp))
                    if fp.suffix in (".py", ".ts", ".js", ".md", ".sql"):
                        files_to_scan.append(fp)
                    if len(files_to_scan) > 1000:
                        break
                if len(files_to_scan) > 1000:
                    break
        else:
            files_to_scan = [p] if p.suffix in (".py", ".ts", ".js", ".md") else []

        for f in files_to_scan[:300]:
            txt = _read_text(f)
            if self.TODO_PAT.search(txt):
                todo_count += len(self.TODO_PAT.findall(txt))
            if self.SECRET_PAT.search(txt):
                secret_count += 1
            # long files
            loc = len([l for l in txt.splitlines() if l.strip()])
            if loc > 500:
                try:
                    rel = str(f.relative_to(root)) if f.is_relative_to(root) else f.name
                except ValueError:
                    rel = f.name
                long_files.append(f"{rel} ({loc} LOC)")

        # missing_tests: módulos sem teste correspondente
        missing_tests: List[str] = []
        if mods and not has_tests:
            missing_tests = [m["name"] for m in mods[:5]]
        elif mods:
            # verifica cada módulo se tem test_ correspondente
            for m in mods:
                mod_name = m["name"]
                # procura test file com nome do módulo
                has_mod_test = any(mod_name.lower() in tf.lower() or tf.startswith("test_") for tf in test_files)
                if not has_mod_test and m["files"] > 2:
                    missing_tests.append(mod_name)

        stale_deps: List[str] = []
        for dep in deps.get("all", []):
            ver = dep.get("version", "").strip()
            if not ver or ver in ("*", "", "latest"):
                stale_deps.append(dep["name"])

        gaps: List[Dict[str, str]] = []
        if todo_count:
            gaps.append({"type": "todo_fixme", "severity": "medium", "description": f"{todo_count} TODO/FIXME/XXX encontrados — débito técnico"})
        if secret_count:
            gaps.append({"type": "hardcoded_secret", "severity": "critical", "description": f"{secret_count} possíveis segredos hardcoded"})
        if not has_readme and p.is_dir():
            gaps.append({"type": "missing_docs", "severity": "medium", "description": "Sem README.md — documentação ausente"})
        if missing_tests:
            gaps.append({"type": "missing_tests", "severity": "high", "description": f"Módulos sem testes: {', '.join(missing_tests[:3])}"})
        if stale_deps:
            gaps.append({"type": "stale_deps", "severity": "low", "description": f"Dependências sem pin: {', '.join(stale_deps[:3])}"})
        if long_files:
            gaps.append({"type": "long_files", "severity": "low", "description": f"Arquivos longos (>500 LOC): {', '.join(long_files[:2])}"})
        if long_files and len(long_files) > 3:
            gaps.append({"type": "complexity", "severity": "medium", "description": f"{len(long_files)} arquivos longos indicam alta complexidade"})

        # Correlações e soluções/inovações
        correlations: List[str] = []
        if todo_count and missing_tests:
            correlations.append("Correlação: TODOs concentrados em módulos sem testes — priorizar testes nesses módulos reduz débito mais rápido")
        if secret_count and not has_readme:
            correlations.append("Correlação: segredos hardcoded + falta de docs sugere onboarding fraco — documentar variáveis de ambiente")
        if stale_deps and long_files:
            correlations.append("Correlação: dependências soltas + arquivos longos — risco de quebra em update; quebrar módulos primeiro")

        solutions: List[str] = []
        if missing_tests:
            solutions.append(f"Criar suites de teste para: {', '.join(missing_tests[:3])} (TDD RED→GREEN)")
        if todo_count:
            solutions.append("Converter TODOs em issues rastreadas e TSPECs com critério de aceitação")
        if secret_count:
            solutions.append("Migrar segredos para .env + validação em CI (gitleaks)")
        if not has_readme:
            solutions.append("Gerar README com arquitetura, instalação e uso (Reversa: inventory.md como base)")
        if stale_deps:
            solutions.append("Fixar versões em requirements.txt/package.json e adicionar pip-audit/dependabot")

        innovations: List[str] = []
        if len(mods) > 5:
            innovations.append("Oportunidade: extrair módulos com >10 arquivos para pacote independente — reduz acoplamento")
        if inv.get("integrations"):
            innovations.append(f"Oportunidade: expor integrações {', '.join(inv['integrations'][:2])} como capability seam (Service Definition/Provider/Consumer)")
        if len(deps.get("all", [])) > 10:
            innovations.append("Oportunidade: gerar SBOM (CycloneDX) a partir do grafo de dependências para auditoria de supply-chain")

        return {
            "gaps": gaps,
            "correlations": correlations,
            "solutions": solutions,
            "innovations": innovations,
            "metrics": {
                "todo_count": todo_count,
                "secret_count": secret_count,
                "has_readme": has_readme,
                "has_tests": has_tests,
                "long_files": len(long_files),
                "stale_deps": len(stale_deps),
                "total_gaps": len(gaps),
            },
        }

    # ── Analyze completo ────────────────────────────────────────────
    def analyze(self, path: str | Path, output_root: Optional[str | Path] = None) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {"target": str(p), "error": f"path não existe: {path}", "inventory": {}, "modules": [], "dependencies": {}, "data_model": [], "gaps": {}, "recommendations": []}

        inv = self.inventory(p)
        mods = self.modules(p)
        deps = self.dependencies(p)
        dm = self.data_model(p)
        gaps_data = self.gaps(p, inv, mods, deps)

        recommendations: List[str] = []
        for g in gaps_data.get("gaps", []):
            recommendations.append(f"[{g['severity']}] {g['type']}: {g['description']}")
        recommendations.extend(gaps_data.get("solutions", []))
        recommendations.extend(gaps_data.get("innovations", []))

        result: Dict[str, Any] = {
            "target": str(p),
            "inventory": inv,
            "modules": mods,
            "dependencies": deps,
            "data_model": dm,
            "gaps": gaps_data,
            "recommendations": recommendations,
            "files_written": [],
        }

        # Escrita opcional em output_root
        if output_root:
            out = Path(output_root)
            try:
                out.mkdir(parents=True, exist_ok=True)
                # inventory.md
                inv_md = out / "inventory.md"
                with open(inv_md, "w", encoding="utf-8") as f:
                    f.write(f"# Inventory — {p.name}\n\n")
                    f.write(f"- **Target**: `{p}`\n")
                    f.write(f"- **Total files**: {inv.get('total_files',0)}\n")
                    f.write(f"- **Total LOC**: {inv.get('total_loc',0)}\n")
                    f.write(f"- **Languages**: {', '.join(inv.get('languages',[])) or '—'}\n")
                    f.write(f"- **Frameworks**: {', '.join(inv.get('frameworks',[])) or '—'}\n")
                    f.write(f"- **Modules**: {len(mods)}\n")
                    f.write(f"- **Dependencies**: {deps.get('count',0)}\n")
                result["files_written"].append(str(inv_md))
                # gaps.md
                gaps_md = out / "gaps.md"
                with open(gaps_md, "w", encoding="utf-8") as f:
                    f.write(f"# Gaps — {p.name}\n\n")
                    for g in gaps_data.get("gaps", []):
                        f.write(f"- **{g['type']}** ({g['severity']}): {g['description']}\n")
                    if gaps_data.get("correlations"):
                        f.write("\n## Correlations\n")
                        for c in gaps_data["correlations"]:
                            f.write(f"- {c}\n")
                    if gaps_data.get("solutions"):
                        f.write("\n## Solutions\n")
                        for s in gaps_data["solutions"]:
                            f.write(f"- {s}\n")
                result["files_written"].append(str(gaps_md))
            except Exception as exc:
                result["write_error"] = str(exc)

        # Publicação no MetaBus (best-effort)
        try:
            from mci.metabus import metabus

            metabus.publish_subsystem_event(
                "reversa_universal",
                "analysis.completed",
                {"target": str(p), "modules": len(mods), "gaps": gaps_data["metrics"]["total_gaps"], "languages": inv.get("languages", [])},
                source_agent="reversa_universal_engine",
            )
            metabus.memory.add_reflection(
                agent_id="reversa_universal",
                task_context=f"análise reversa: {p}",
                reflection=f"Reversa analisou {p}: {len(mods)} módulos, {gaps_data['metrics']['total_gaps']} gaps, {inv.get('total_loc',0)} LOC.",
                score=min(1.0, 0.5 + len(mods) * 0.05),
            )
        except Exception:
            pass

        return result

    # ── Enhancements para raciocínio/pesquisa/manuscrito ────────────
    def enhance_reasoning(self, context: Dict[str, Any], analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enriquece contexto de raciocínio com estrutura Reversa."""
        if analysis is None:
            return context
        enriched = dict(context)
        enriched["reversa_modules"] = [m["name"] for m in analysis.get("modules", [])[:5]]
        enriched["reversa_gaps"] = [g["type"] for g in analysis.get("gaps", {}).get("gaps", [])[:5]]
        enriched["reversa_correlations"] = analysis.get("gaps", {}).get("correlations", [])[:2]
        return enriched

    def enhance_research(self, query: str, analysis: Optional[Dict[str, Any]] = None) -> str:
        """Expande query de pesquisa com termos de módulos/gaps."""
        if not analysis or not isinstance(query, str):
            return query
        terms: List[str] = []
        for m in analysis.get("modules", [])[:3]:
            terms.extend(m.get("classes", [])[:2])
            terms.extend(m.get("functions", [])[:2])
        # filtra termos relevantes (evita genéricos)
        terms = [t for t in terms if len(t) > 4][:5]
        if terms:
            return f"{query} {' '.join(terms)}"
        return query

    def enhance_manuscript(self, sections: Dict[str, str], analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sugere seções faltantes baseado em gaps."""
        if not analysis:
            return {"suggestions": [], "enhanced": sections}
        gaps = analysis.get("gaps", {}).get("gaps", [])
        gap_types = {g["type"] for g in gaps}
        suggestions: List[str] = []
        if "missing_docs" in gap_types and "arquitetura" not in " ".join(sections.keys()).lower():
            suggestions.append("Adicionar seção de Arquitetura (Reversa detectou falta de docs)")
        if "missing_tests" in gap_types and "limitações" not in " ".join(sections.keys()).lower():
            suggestions.append("Adicionar Limitações/Testes (módulos sem testes detectados)")
        if "hardcoded_secret" in gap_types:
            suggestions.append("Adicionar seção de Segurança/Ética (segredos hardcoded)")
        return {"suggestions": suggestions, "enhanced": sections, "gaps_considered": list(gap_types)}


# Singleton
reversa_engine = ReversaUniversalEngine()
