"""
Demo: Subsistema de Ilustrações + FigureHunter.
Executa os três motores de ilustração (Mermaid, Graphify, MIRA) e a
extração de figuras reais dos PDFs da produção científica existente.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from illustrations import MermaidEngine, GraphifyEngine, MiraEngine
from research.figure_hunter import FigureHunter


def main() -> None:
    out = ROOT / "producao_cientifica" / "demo-ilustracoes"
    print("=" * 70)
    print("DEMO: Ilustrações Científicas (Mermaid + Graphify + MIRA + Figuras)")
    print("=" * 70)

    # 1. Mermaid ---------------------------------------------------------
    me = MermaidEngine(output_dir=str(out / "ilustracoes"))
    fig = me.flowchart(
        "Pipeline Metacognitivo",
        [("Percepção HTM", "Especificação SDD"), ("Especificação SDD", "Atenção Multi-Head"),
         ("Atenção Multi-Head", "Execução TDD"), ("Execução TDD", "Reflexão MCI")],
        caption="Ciclo de vida de uma tarefa no orquestrador marceloclaro",
    )
    me.render(fig)
    mm = me.mindmap("Ecossistema", "OpenCode Core",
                    {"Metacognição": ["MetaBus", "Reflexion"],
                     "Produção": ["LaTeX Modular", "KDP"],
                     "Pesquisa": ["arXiv", "Fichamentos"]})
    me.render(mm)
    print(f"\n[1] Mermaid: {fig.image_path or fig.mmd_path}")
    print(f"    Mindmap: {mm.image_path or mm.mmd_path}")

    # 2. Graphify --------------------------------------------------------
    texts = {}
    prod = ROOT / "producao_cientifica"
    for md in list(prod.rglob("pesquisa/md/*.md"))[:4]:
        texts[md.stem] = md.read_text(encoding="utf-8", errors="ignore")[:20000]
    if not texts:
        texts = {"exemplo": "orquestração metacognitiva agentes memória atenção " * 50}
    ge = GraphifyEngine(output_dir=str(out / "ilustracoes" / "grafo"))
    graph = ge.build(texts)
    paths = ge.export(graph)
    print(f"\n[2] Graphify: {len(graph.nodes)} nós, {len(graph.edges)} arestas")
    print(f"    Exportado: {paths['html']}")

    # 3. MIRA ------------------------------------------------------------
    mi = MiraEngine(output_dir=str(out / "ilustracoes" / "mira"))
    cards = mi.illustrate_sections({
        "Orquestração de Agentes": "coordenação multiagente com maestro central",
        "Pipeline de Produção": "fluxo de etapas da pesquisa até o livro",
        "Janela de Contexto": "memória limitada onde o novo empurra o antigo",
    })
    print(f"\n[3] MIRA: {len(cards)} cards animados gerados")
    for c in cards:
        print(f"    - {c.title} -> metáfora: {c.metaphor.scene}")

    # 4. FigureHunter ----------------------------------------------------
    hunter = FigureHunter()
    total = []
    for prod_dir in sorted(prod.glob("*/")):
        if (prod_dir / "pesquisa" / "pdfs").exists():
            figs = hunter.harvest_production(str(prod_dir))
            if figs:
                total.extend(figs)
                print(f"\n[4] {prod_dir.name}: {len(figs)} figuras reais extraídas")
                print(f"    Catálogo: {prod_dir / 'pesquisa' / 'imagens' / 'FONTES.md'}")
                for f in figs[:3]:
                    print(f"    - {Path(f.image_path).name} (p.{f.page}) | ABNT: {f.abnt()[:70]}...")
                break  # uma produção basta para a demo
    if not total:
        print("\n[4] Nenhum PDF disponível para extração (rode demo_research.py antes).")

    print("\n" + "=" * 70)
    print("Demo concluída.")
    print("=" * 70)


if __name__ == "__main__":
    main()
