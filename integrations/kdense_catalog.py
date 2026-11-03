"""Catálogo local das 177 instruções K-Dense, sob demanda e sem execução.

O espelho contém apenas SKILL.md e metadados. Scripts, assets e dependências do
repositório original não são copiados nem executados. `external/` não é um
diretório de skills auto-carregadas.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "external/kdense-scientific-agent-skills/CATALOG.json"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")


def load_catalog(path: Path | str | None = None) -> dict:
    path = Path(path or CATALOG_PATH)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("count") != 177:
        raise ValueError("catálogo K-Dense inválido: esperado schema 1/count 177")
    skills = data.get("skills")
    if not isinstance(skills, list) or len(skills) != 177:
        raise ValueError("catálogo K-Dense deve ter 177 entradas")
    names = [item.get("skill") for item in skills]
    if len(set(names)) != 177 or not all(isinstance(n, str) and NAME.fullmatch(n)
                                          for n in names):
        raise ValueError("nomes de skills inválidos ou duplicados")
    return data


def category_counts(catalog: dict) -> dict:
    counts = {}
    for item in catalog["skills"]:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    if sum(counts.values()) != 177:
        raise ValueError("soma de categorias difere de 177")
    return dict(sorted(counts.items()))


def _normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9áàâãéêíóôõúüç -]+", " ",
                           value.casefold()).split())


def search(catalog: dict, query: str, *, category: str | None = None,
           limit: int = 20) -> list[dict]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("consulta obrigatória")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limite deve ser 1..100")
    if category is not None and category not in category_counts(catalog):
        raise ValueError(f"categoria desconhecida: {category}")
    tokens = _normalize(query).split()
    results = []
    for item in catalog["skills"]:
        if category and item["category"] != category:
            continue
        haystack = _normalize(" ".join([
            item["skill"], item["description"], item["category"],
            " ".join(item.get("risk_flags", []))]))
        score = sum(2 if token in _normalize(item["skill"]) else 1 if token in haystack else 0
                    for token in tokens)
        if score:
            results.append((score, item["skill"], item))
    results.sort(key=lambda row: (-row[0], row[1]))
    return [{**item, "score": score} for score, _, item in results[:limit]]


def get_skill(catalog: dict, name: str) -> dict:
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("nome de skill inválido")
    item = next((row for row in catalog["skills"] if row["skill"] == name), None)
    if item is None:
        raise ValueError(f"skill não catalogada: {name}")
    if not item.get("mirrored") or not item.get("local_skill_md"):
        raise ValueError(f"skill em license_hold; consulte a fonte: {item.get('source_url')}")
    relative = Path(item["local_skill_md"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("caminho local inválido")
    target = (CATALOG_PATH.parent / relative).resolve()
    root = CATALOG_PATH.parent.resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError("SKILL.md local ausente ou fora da raiz")
    return {**item, "path": str(target), "text": target.read_text(encoding="utf-8")}


def stats(catalog: dict) -> dict:
    flags = {}
    for item in catalog["skills"]:
        for flag in item.get("risk_flags", []):
            flags[flag] = flags.get(flag, 0) + 1
    return {
        "count": catalog["count"],
        "categories": category_counts(catalog),
        "risk_flags": dict(sorted(flags.items())),
        "permissive_count": sum(1 for x in catalog["skills"] if x.get("license_class") == "permissive"),
        "license_hold_count": sum(1 for x in catalog["skills"] if x.get("license_class") == "hold"),
        "instruction_only": sum(1 for x in catalog["skills"] if x.get("instruction_only")),
        "scripts_vendored": sum(1 for x in catalog["skills"] if x.get("scripts_vendored")),
        "autoload": sum(1 for x in catalog["skills"] if x.get("autoload")),
        "source_commit": catalog["commit"],
        "license": catalog["license"],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("stats")
    p = sub.add_parser("categories")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--category")
    p.add_argument("--limit", type=int, default=20)
    p = sub.add_parser("show")
    p.add_argument("name")
    p.add_argument("--full", action="store_true")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        if args.command == "stats":
            print(json.dumps(stats(catalog), ensure_ascii=False, indent=2))
        elif args.command == "categories":
            counts = category_counts(catalog)
            print(json.dumps(counts, ensure_ascii=False, indent=2) if args.json else
                  "\n".join(f"{name}: {count}" for name, count in counts.items()))
        elif args.command == "search":
            rows = search(catalog, args.query, category=args.category, limit=args.limit)
            print(json.dumps([{k: row[k] for k in
                               ("skill", "category", "description", "risk_flags", "score")}
                              for row in rows], ensure_ascii=False, indent=2))
        else:
            row = get_skill(catalog, args.name)
            print(json.dumps({k: row[k] for k in
                              ("skill", "category", "description", "source_url",
                               "source_commit", "risk_flags", "status")},
                             ensure_ascii=False, indent=2))
            text = row["text"] if args.full else row["text"][:12000]
            print("\n" + text)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)},
                         ensure_ascii=False, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
