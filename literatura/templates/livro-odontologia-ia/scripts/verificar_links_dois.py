#!/usr/bin/env python3
"""
Verificador de DOIs e Links do Livro
======================================
Script que percorre o arquivo .bib e verifica se cada DOI
é válido através de requisições HEAD ao doi.org.

Uso:
    python scripts/verificar_links_dois.py
    python scripts/verificar_links_dois.py --bib referencias/bibliografia.bib
"""

import argparse
import re
import sys
from urllib import request, error
from pathlib import Path


# Constantes
TIMEOUT = 10  # segundos
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) LivroOdontologiaIA/1.0"


def extrair_dois(caminho_bib: Path):
    """Extrai todos os DOIs de um arquivo .bib."""
    dois_encontrados = []
    doi_pattern = re.compile(r"doi\s*=\s*\{([^}]+)\}")

    try:
        with open(caminho_bib, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_bib}")
        sys.exit(1)

    matches = doi_pattern.findall(conteudo)
    for doi in matches:
        doi = doi.strip()
        dois_encontrados.append(doi)

    return dois_encontrados


def verificar_doi(doi: str) -> dict:
    """Verifica se um DOI é acessível via doi.org."""
    url = f"https://doi.org/{doi}"
    req = request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf"},
        method="HEAD",
    )

    resultado = {
        "doi": doi,
        "url": url,
        "valido": False,
        "status_code": None,
        "erro": None,
    }

    try:
        with request.urlopen(req, timeout=TIMEOUT) as resp:
            resultado["valido"] = True
            resultado["status_code"] = resp.status
    except error.HTTPError as e:
        resultado["status_code"] = e.code
        if e.code == 404:
            resultado["erro"] = "DOI não encontrado (404)"
        elif e.code == 403:
            resultado["erro"] = "Acesso proibido (403)"
        else:
            resultado["erro"] = f"HTTP {e.code}"
    except error.URLError as e:
        resultado["erro"] = f"Erro de URL: {e.reason}"
    except Exception as e:
        resultado["erro"] = str(e)

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description="Verificador de DOIs do livro Odontologia & IA"
    )
    parser.add_argument(
        "--bib",
        type=Path,
        default=Path("referencias/bibliografia.bib"),
        help="Caminho para o arquivo .bib (default: referencias/bibliografia.bib)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("VERIFICADOR DE DOIs")
    print(f"Arquivo: {args.bib}")
    print("=" * 60)

    dois = extrair_dois(args.bib)
    if not dois:
        print("⚠️  Nenhum DOI encontrado no arquivo.")
        sys.exit(0)

    print(f"🔍 Encontrados {len(dois)} DOI(s) para verificar.\n")

    resultados = []
    for i, doi in enumerate(dois, 1):
        print(f"  [{i}/{len(dois)}] Verificando: {doi[:60]}...", end=" ")
        sys.stdout.flush()
        resultado = verificar_doi(doi)
        resultados.append(resultado)
        if resultado["valido"]:
            print("✅ OK")
        else:
            print(f"❌ {resultado['erro']}")

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    total = len(resultados)
    validos = sum(1 for r in resultados if r["valido"])
    invalidos = total - validos
    print(f"✅ DOIs válidos: {validos}/{total}")
    if invalidos > 0:
        print(f"❌ DOIs inválidos: {invalidos}/{total}")
        for r in resultados:
            if not r["valido"]:
                print(f"   - {r['doi']} ({r['erro']})")
        sys.exit(1)
    else:
        print("✅ Todos os DOIs estão válidos!")
        print("=" * 60)


if __name__ == "__main__":
    main()