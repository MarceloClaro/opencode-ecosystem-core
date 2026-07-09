#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEEKER → criador-artigo Bridge
Conecta outputs de pesquisa do SEEKER ao pipeline MASWOS Agent Executor.

Uso:
  python seeker_bridge.py from-seeker <seeker_artifacts_dir> --level 2
  python seeker_bridge.py from-editais <edital_id> --level 2
  python seeker_bridge.py list-seeker-runs
  python seeker_bridge.py validate-apa <arquivo.md>
  python seeker_bridge.py apa-report <arquivo.md>
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

CRIADOR_DIR = Path(__file__).resolve().parent
SEEKER_DIR = CRIADOR_DIR.parent / "basis-research"
OUTPUT_DIR = CRIADOR_DIR / "output"

# Importa módulo APA se disponível
try:
    from apa_integration import APAIntegration
    APA_AVAILABLE = True
except ImportError:
    APA_AVAILABLE = False


class SeekerBridge:
    """Bridge entre SEEKER e criador-artigo."""

    @staticmethod
    def list_seeker_runs() -> list[dict]:
        """Lista runs disponiveis do SEEKER."""
        artifacts_dir = SEEKER_DIR / "artifacts"
        if not artifacts_dir.exists():
            return []

        runs = {}
        for f in sorted(artifacts_dir.glob("RUN-*")):
            # Extract run ID from filename
            parts = f.stem.split("_")
            run_id = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]
            if run_id not in runs:
                runs[run_id] = {"run_id": run_id, "files": [], "first_file": f.stem}
            runs[run_id]["files"].append(f.stem)

        return list(runs.values())

    @staticmethod
    def load_seeker_outputs(run_id: Optional[str] = None) -> dict:
        """Carrega outputs de uma run do SEEKER."""
        artifacts_dir = SEEKER_DIR / "artifacts"
        if not artifacts_dir.exists():
            return {}

        outputs = {}
        for f in sorted(artifacts_dir.glob("*.md")):
            if run_id and run_id not in f.stem:
                continue
            content = f.read_text(encoding="utf-8")
            agent_type = f.stem.split("_", 2)[-1] if "_" in f.stem else f.stem
            outputs[agent_type] = {
                "file": f.name,
                "content": content[:5000],
                "size": len(content),
            }

        return outputs

    @staticmethod
    def build_article_prompt(seeker_outputs: dict, tema: str, level: int = 2) -> str:
        """Constroi um prompt de artigo combinando outputs do SEEKER."""
        parts = [
            f"# Artigo Cientifico: {tema}\n",
            f"## Nivel: {level}\n",
            "## Fontes de Pesquisa (SEEKER)\n\n",
        ]

        for agent_type, data in seeker_outputs.items():
            label = agent_type.replace("_", " ").title()
            parts.append(f"### {label}\n{data['content'][:2000]}\n\n")

        parts.append(
            "## Instrucao\n"
            "Produza um artigo cientifico completo em Portugues Brasileiro formal "
            "utilizando as pesquisas acima como fundamentacao.\n"
        )

        return "\n".join(parts)

    @staticmethod
    def feed_to_maswos(tema: str, seeker_outputs: dict, level: int = 2) -> dict:
        """Alimenta outputs do SEEKER no MASWOS Agent Executor."""
        sys.path.insert(0, str(CRIADOR_DIR))
        from executor import AgentExecutor

        executor = AgentExecutor(tema=tema, level=level)

        # Add seeker outputs as initial context
        seeker_summary = {}
        for agent_type, data in seeker_outputs.items():
            seeker_summary[agent_type] = data["content"][:3000]

        executor.state.outputs["_seeker"] = json.dumps(seeker_summary, ensure_ascii=False)

        # Run the pipeline
        result = executor.run_full()
        return result


def cmd_from_seeker(seeker_run_id: str, level: int = 2):
    """Executa pipeline a partir de outputs do SEEKER."""
    bridge = SeekerBridge()
    outputs = bridge.load_seeker_outputs(seeker_run_id)

    if not outputs:
        print(f"Nenhum output encontrado para run {seeker_run_id}")
        return

    # Try to infer tema from first output
    first = list(outputs.values())[0]
    tema = first["content"][:200].split("\n")[0] if first["content"] else "Pesquisa Academica"
    tema = tema.replace("#", "").strip()[:80]

    print(f"Run SEEKER: {seeker_run_id}")
    print(f"Agents: {len(outputs)}")
    print(f"Tema inferido: {tema}")
    print(f"Nivel: {level}")
    print()

    result = bridge.feed_to_maswos(tema, outputs, level)

    print(json.dumps({
        "status": "completed",
        "seeker_run": seeker_run_id,
        "tema": tema,
        "agents_executed": result.get("agents_executed", 0),
        "output_dir": result.get("output_dir"),
    }, ensure_ascii=False, indent=2))


def cmd_list_seeker_runs():
    """Lista runs do SEEKER."""
    runs = SeekerBridge.list_seeker_runs()
    if not runs:
        print("Nenhuma run do SEEKER encontrada.")
        return

    print(f"\nRuns do SEEKER disponiveis ({len(runs)}):")
    print("-" * 60)
    for r in runs:
        print(f"  {r['run_id']} ({len(r['files'])} arquivos)")
    print()


def cmd_from_editais(edital_id: str, level: int = 2):
    """Executa pipeline a partir de um edital especifico."""
    # Busca edital no editais-local
    import subprocess
    try:
        result = subprocess.run(
            ["editais-local", "semantic-search", edital_id, "--k", "1"],
            capture_output=True, text=True, timeout=30,
        )
        tema = f"Edital {edital_id}: {result.stdout[:100] if result.stdout else edital_id}"
    except Exception:
        tema = f"Analise de Edital: {edital_id}"

    # Create minimal seeker-style output
    seeker_outputs = {
        "editais_context": {
            "file": f"edital_{edital_id}",
            "content": f"Edital ID: {edital_id}\nContexto: {tema}",
            "size": len(tema),
        }
    }

    result = SeekerBridge.feed_to_maswos(tema, seeker_outputs, level)
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ─── APA Integration Commands ─────────────────────────────────────

def cmd_validate_apa(file_path: str):
    """Valida um arquivo quanto às normas APA."""
    if not APA_AVAILABLE:
        print("ERRO: Modulo apa_integration nao encontrado.")
        print("Certifique-se de que o arquivo apa_integration.py esta no diretorio.")
        return
    
    apa = APAIntegration()
    result = apa.validate_document(file_path)
    
    print(f"\n{'='*60}")
    print(f"VALIDACAO APA - {file_path}")
    print(f"{'='*60}")
    print(f"Pontuacao: {result.score:.1f}/100")
    print(f"Status: {'CONFORME' if result.is_compliant else 'NAO CONFORME'}")
    print(f"Secoes encontradas: {len(result.sections_found)}/{len(apa.pf_sections)}")
    print(f"Citacoes: {result.citations_count}")
    print(f"Referencias: {result.references_count}")
    
    if result.issues:
        print(f"\nProblemas ({len(result.issues)}):")
        for issue in result.issues:
            print(f"  - {issue}")
    
    if result.warnings:
        print(f"\nAlertas ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    print(f"{'='*60}\n")


def cmd_apa_report(file_path: str):
    """Gera relatorio completo de conformidade APA."""
    if not APA_AVAILABLE:
        print("ERRO: Modulo apa_integration nao encontrado.")
        return
    
    apa = APAIntegration()
    result = apa.validate_document(file_path)
    report = apa.generate_apa_report(result)
    print(report)


def cmd_validate_citations(file_path: str):
    """Valida apenas as citacoes de um arquivo."""
    if not APA_AVAILABLE:
        print("ERRO: Modulo apa_integration nao encontrado.")
        return
    
    apa = APAIntegration()
    content = Path(file_path).read_text(encoding='utf-8')
    result = apa.validate_citations_in_text(content)
    
    print(f"\nValidacao de Citacoes - {file_path}")
    print(f"Total: {result['summary']['total']}")
    print(f"Validas: {result['summary']['valid']}")
    print(f"Invalidas: {result['summary']['invalid']}")
    print(f"Conformidade: {result['summary']['compliance_rate']:.1f}%")


def cmd_validate_references(file_path: str):
    """Valida a secao de referencias de um arquivo."""
    if not APA_AVAILABLE:
        print("ERRO: Modulo apa_integration nao encontrado.")
        return
    
    apa = APAIntegration()
    content = Path(file_path).read_text(encoding='utf-8')
    result = apa._validate_references(content)
    
    print(f"\nValidacao de Referencias - {file_path}")
    print(f"Total: {result['total']}")
    print(f"Validas: {result['valid']}")
    print(f"Conformidade: {result['compliance_rate']:.1f}%")


def cmd_format_citation():
    """Formata uma citacao APA interativamente."""
    if not APA_AVAILABLE:
        print("ERRO: Modulo apa_integration nao encontrado.")
        return
    
    apa = APAIntegration()
    
    print("\nFormatacao de Citacao APA")
    print("-" * 40)
    
    citation_type = input("Tipo (narrative/parenthetical): ").strip() or "parenthetical"
    authors_input = input("Autores (separados por virgula): ").strip()
    authors = [a.strip() for a in authors_input.split(",")] if authors_input else ["Autor"]
    year = input("Ano: ").strip() or str(datetime.now().year)
    title = input("Titulo (opcional): ").strip()
    page = input("Pagina (opcional): ").strip()
    
    result = apa.format_citation(citation_type, authors, year, title, page)
    print(f"\nCitacao formatada:\n  {result}")


def cmd_format_reference():
    """Formata uma referencia APA interativamente."""
    if not APA_AVAILABLE:
        print("ERRO: Modulo apa_integration nao encontrado.")
        return
    
    apa = APAIntegration()
    
    print("\nFormatacao de Referencia APA")
    print("-" * 40)
    print("Tipos: book, article, website, chapter, thesis")
    
    ref_type = input("Tipo: ").strip() or "book"
    authors_input = input("Autores (separados por virgula): ").strip()
    authors = [a.strip() for a in authors_input.split(",")] if authors_input else ["Autor"]
    year = input("Ano: ").strip() or str(datetime.now().year)
    title = input("Titulo: ").strip() or "Titulo nao informado"
    
    kwargs = {'authors': authors, 'year': year, 'title': title}
    
    if ref_type == "book":
        kwargs['publisher'] = input("Editora: ").strip() or "Editora nao informada"
    elif ref_type == "article":
        kwargs['journal'] = input("Periodico: ").strip() or "Periodico nao informado"
        kwargs['volume'] = input("Volume: ").strip()
        kwargs['issue'] = input("Numero: ").strip()
        kwargs['pages'] = input("Paginas: ").strip()
        kwargs['doi'] = input("DOI: ").strip()
    elif ref_type == "website":
        kwargs['url'] = input("URL: ").strip()
    elif ref_type == "chapter":
        kwargs['book_title'] = input("Titulo do livro: ").strip()
        kwargs['editors'] = [input("Editor(es): ").strip() or "Editor"]
        kwargs['pages'] = input("Paginas: ").strip()
        kwargs['publisher'] = input("Editora: ").strip()
    elif ref_type == "thesis":
        kwargs['institution'] = input("Instituicao: ").strip()
        kwargs['thesis_type'] = input("Tipo (Tese/Dissertacao): ").strip() or "Tese"
    
    result = apa.format_reference(ref_type, **kwargs)
    print(f"\nReferencia formatada:\n  {result}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "from-seeker":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py from-seeker <seeker_artifacts_dir> [--level N]")
            return
        run_id = sys.argv[2]
        level = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--level" else 2
        cmd_from_seeker(run_id, level)

    elif cmd == "from-editais":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py from-editais <edital_id> [--level N]")
            return
        edital_id = sys.argv[2]
        level = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--level" else 2
        cmd_from_editais(edital_id, level)

    elif cmd == "list-seeker-runs":
        cmd_list_seeker_runs()

    elif cmd == "validate-apa":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py validate-apa <arquivo.md>")
            return
        cmd_validate_apa(sys.argv[2])

    elif cmd == "apa-report":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py apa-report <arquivo.md>")
            return
        cmd_apa_report(sys.argv[2])

    elif cmd == "validate-citations":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py validate-citations <arquivo.md>")
            return
        cmd_validate_citations(sys.argv[2])

    elif cmd == "validate-references":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py validate-references <arquivo.md>")
            return
        cmd_validate_references(sys.argv[2])

    elif cmd == "format-citation":
        cmd_format_citation()

    elif cmd == "format-reference":
        cmd_format_reference()

    else:
        print(f"Unknown command: {cmd}")
        print("Available commands:")
        print("  from-seeker         - Execute pipeline from SEEKER outputs")
        print("  from-editais        - Execute pipeline from edital")
        print("  list-seeker-runs    - List available SEEKER runs")
        print("  validate-apa        - Validate document APA compliance")
        print("  apa-report          - Generate full APA compliance report")
        print("  validate-citations  - Validate citations only")
        print("  validate-references - Validate references only")
        print("  format-citation     - Format a citation interactively")
        print("  format-reference    - Format a reference interactively")


if __name__ == "__main__":
    main()
