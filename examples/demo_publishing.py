"""Demo: pipeline de pasta única de produção científica (LaTeX+PDF+DOCX+MD+ODT)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from publishing import ScientificProduction, list_templates  # noqa: E402

CONTENT = """## Introdução

Este manuscrito demonstra o pipeline de produção científica do OpenCode
Ecosystem Core, com a fórmula $E = mc^2$ formatada em ambiente matemático,
e a estrutura canônica de pasta única contendo todos os compilados.

## Metodologia

O pipeline converte a fonte Markdown canônica em LaTeX (template Qualis A1),
e compila os formatos PDF, DOCX e ODT (compatível com Amazon KDP), gerando
um manifesto auditável com checksums SHA-256 de cada artefato.

## Conclusão

A pasta única garante rastreabilidade completa da produção, do fonte ao
compilado, atendendo ao rigor de reprodutibilidade Qualis A1.
"""


def main() -> None:
    print("=== Templates disponíveis ===")
    for name, path in list_templates().items():
        print(f"  {name}: {os.path.relpath(path)}")

    print("\n=== Construindo produção (template: artigo) ===")
    prod = ScientificProduction(
        title="Demo do Pipeline de Producao Cientifica", template="artigo"
    )
    manifest = prod.build(CONTENT)

    print(f"Pasta: {manifest['folder']}")
    for fmt, info in manifest["formats"].items():
        status = f"OK ({info['bytes']} bytes)" if info else "NÃO GERADO"
        print(f"  {fmt}: {status}")
    print(f"KDP-ready (ODT): {manifest['kdp_ready']}")
    print("\nLog do build:")
    for line in manifest["log"]:
        print(f"  - {line}")


if __name__ == "__main__":
    main()
