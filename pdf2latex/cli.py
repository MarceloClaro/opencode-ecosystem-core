"""
Interface de linha de comando para o PDF2LaTeX.
Permite executar o pipeline completo com opções.
"""

import argparse
import sys
from pathlib import Path

from . import PDF2LaTeX
from .template_integrator import TEMPLATE_CLASS


def main():
    """Ponto de entrada da CLI."""
    parser = argparse.ArgumentParser(
        description="PDF2LaTeX — Converte PDF para projeto LaTeX completo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 -m pdf2latex documento.pdf
  python3 -m pdf2latex documento.pdf --template abntex2 --output ./meu-projeto
  python3 -m pdf2latex documento.pdf --template ieee --with-tables --no-equations
  python3 -m pdf2latex documento.pdf --ocr --ocr-lang por
  python3 -m pdf2latex documento.pdf --verbose --compile
        """,
    )

    parser.add_argument("pdf", nargs="?", default=None,
                        help="Caminho para o arquivo PDF de entrada")
    parser.add_argument("-o", "--output", default=None,
                        help="Diretório de saída do projeto LaTeX")
    parser.add_argument("-t", "--template", default=None,
                        help="Template LaTeX a aplicar (ex: abntex2, ieee, acm, nature)")
    parser.add_argument("--ocr", action="store_true",
                        help="Usar OCR para PDFs escaneados")
    parser.add_argument("--ocr-lang", default="por+eng",
                        help="Idioma para OCR (padrão: por+eng)")
    parser.add_argument("--no-tables", action="store_true",
                        help="Pular detecção de tabelas")
    parser.add_argument("--no-equations", action="store_true",
                        help="Pular detecção de equações")
    parser.add_argument("--no-references", action="store_true",
                        help="Pular extração de referências")
    parser.add_argument("--no-images", action="store_true",
                        help="Pular extração de imagens")
    parser.add_argument("--compile", action="store_true",
                        help="Compilar projeto após gerar")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Modo verboso (debug)")
    parser.add_argument("--list-templates", action="store_true",
                        help="Listar templates disponíveis e sair")

    args = parser.parse_args()

    # Listar templates
    if args.list_templates:
        print("=" * 60)
        print("📋 TEMPLATES LaTeX DISPONÍVEIS")
        print("=" * 60)
        print()
        print("🇧🇷  ACADÊMICOS BRASILEIROS")
        print("-" * 40)
        templates_br = [
            ("abntex2", "abnTeX2 — 8 modelos ABNT"),
            ("abnt2025", "ABNT 2025 — normas atualizadas"),
            ("unb-monografia", "Monografia DCC/CIC-UnB"),
            ("usp", "Modelo USP"),
            ("icmc", "ICMC-USP"),
            ("ipleiria", "IPLeiria Portugal"),
            ("capes", "Modelo CAPES"),
            ("artigo-qualis-a1", "Artigo Qualis A1"),
        ]
        for name, desc in templates_br:
            print(f"  {name:25s} {desc}")

        print()
        print("🌍  INTERNACIONAIS")
        print("-" * 40)
        templates_intl = [
            ("acm", "ACM — Association for Computing Machinery"),
            ("ieee", "IEEE — conferências e transactions"),
            ("elsevier", "Elsevier — periódicos"),
            ("nature", "Nature Portfolio"),
            ("springer", "Springer Nature"),
            ("tandf", "Taylor & Francis"),
            ("mdpi", "MDPI"),
            ("sbc", "SBC — Sociedade Brasileira de Computação"),
        ]
        for name, desc in templates_intl:
            print(f"  {name:25s} {desc}")

        print()
        print("📖  LIVROS")
        print("-" * 40)
        templates_livro = [
            ("victoria-regia", "Victoria Regia — e-book clássico"),
            ("book-simple", "Livro simples"),
            ("lathex-dark", "Tema escuro"),
        ]
        for name, desc in templates_livro:
            print(f"  {name:25s} {desc}")

        print()
        print("📄  CURRÍCULOS")
        print("-" * 40)
        print("  latexcv                 10 estilos de currículo")
        print()
        print("Use: python3 -m pdf2latex documento.pdf --template <nome>")
        return

    # Validar
    if not args.pdf:
        parser.print_help()
        sys.exit(1)
    if not Path(args.pdf).exists():
        print(f"❌ Erro: PDF não encontrado: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    # Executar conversão
    try:
        converter = PDF2LaTeX(
            pdf_path=args.pdf,
            output_dir=args.output or f"./{Path(args.pdf).stem}_latex",
            template=args.template,
            ocr=args.ocr,
            ocr_lang=args.ocr_lang,
            extract_tables=not args.no_tables,
            extract_equations=not args.no_equations,
            extract_references=not args.no_references,
            extract_images=not args.no_images,
            verbose=args.verbose,
        )
        output_dir = converter.convert()

        print()
        print("=" * 60)
        print(f"✅ PROJETO GERADO: {output_dir}")
        print("=" * 60)
        print()
        print("📁 Estrutura do projeto:")
        print(f"   {output_dir}/")
        print(f"   ├── main.tex")
        print(f"   ├── Makefile")
        print(f"   ├── referencias.bib")
        print(f"   ├── capitulos/")
        print(f"   └── figures/")
        print()
        print("🚀 Para compilar:")
        print(f"   cd {output_dir} && make")
        print()

        if args.compile:
            print("🔧 Compilando...")
            converter.compile()

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
