#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integracao APA
Verifica se o modulo APA esta funcionando corretamente.
"""

import sys
from pathlib import Path

# Adiciona o diretorio atual ao path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from apa_integration import APAIntegration, CitationResult, ReferenceResult, DocumentValidation
    print("[OK] Modulo apa_integration importado com sucesso")
except ImportError as e:
    print(f"[ERRO] Erro ao importar apa_integration: {e}")
    sys.exit(1)


def test_citation_validation():
    """Testa validacao de citacoes"""
    print("\n[TESTE] Validacao de Citacoes")
    print("-" * 50)
    
    apa = APAIntegration()
    
    # Citacoes validas
    valid_citations = [
        "(Silva, 2020)",
        "Silva (2020)",
        "(Silva & Santos, 2021)",
        "Silva e Santos (2021)",
        "(Silva et al., 2022)",
    ]
    
    # Citacoes invalidas
    invalid_citations = [
        "[1]",
        "[2, 3, 4]",
        "Silva 2020",
        "(Silva, 2020, p. 45)",  # Valida mas com pagina
    ]
    
    print("Citacoes validas:")
    for citation in valid_citations:
        result = apa.validate_citation(citation)
        status = "[OK]" if result.is_valid else "[FALHA]"
        print(f"  {status} {citation} -> {result.citation_type}")
    
    print("\nCitacoes invalidas:")
    for citation in invalid_citations:
        result = apa.validate_citation(citation)
        status = "[OK]" if result.is_valid else "[FALHA]"
        print(f"  {status} {citation} -> {result.issues[0] if result.issues else 'OK'}")


def test_citation_formatting():
    """Testa formatacao de citacoes"""
    print("\n[TESTE] Formatacao de Citacoes")
    print("-" * 50)
    
    apa = APAIntegration()
    
    # Teste citacao narrativa
    result = apa.format_citation(
        "narrative",
        ["Silva"],
        "2020",
        "Pesquisa qualitativa"
    )
    print(f"Narrativa: {result}")
    
    # Teste citacao parentetica
    result = apa.format_citation(
        "parenthetical",
        ["Silva", "Santos"],
        "2021",
        page="45"
    )
    print(f"Parentetica: {result}")
    
    # Teste citacao com et al.
    result = apa.format_citation(
        "parenthetical",
        ["Silva", "Santos", "Oliveira"],
        "2022"
    )
    print(f"Et al.: {result}")


def test_reference_formatting():
    """Testa formatacao de referencias"""
    print("\n[TESTE] Formatacao de Referencias")
    print("-" * 50)
    
    apa = APAIntegration()
    
    # Livro
    result = apa.format_reference(
        "book",
        authors=["Silva, A. B."],
        year="2020",
        title="Metodologia da Pesquisa Cientifica",
        publisher="Editora Universitaria"
    )
    print(f"Livro: {result}")
    
    # Artigo
    result = apa.format_reference(
        "article",
        authors=["Santos, C. D.", "Lima, G. H."],
        year="2021",
        title="Impacto da Tecnologia na Educacao",
        journal="Revista de Educacao",
        volume="15",
        issue="3",
        pages="123-145",
        doi="10.1234/edu.2021.001"
    )
    print(f"Artigo: {result}")
    
    # Website
    result = apa.format_reference(
        "website",
        authors=["Empresa ABC"],
        year="2023",
        title="Relatorio Anual",
        url="https://www.empresa.com.br/relatorio"
    )
    print(f"Website: {result}")


def test_document_validation():
    """Testa validacao de documento"""
    print("\n[TESTE] Validacao de Documento")
    print("-" * 50)
    
    apa = APAIntegration()
    
    # Cria um arquivo de teste
    test_content = """# Introducao

Este e um documento de teste para validacao APA.

## Marco Teorico

Segundo Silva (2020), a pesquisa qualitativa e importante.

De acordo com Santos e Lima (2021), os metodos mistos sao eficazes.

## Metodologia

A metodologia utilizada foi a pesquisa qualitativa.

## Resultados

Os resultados foram satisfatorios.

## Discussao

Os resultados confirmam a hipotese inicial.

## Conclusoes

O estudo demonstrou a importancia da pesquisa.

## Referencias

Silva, A. B. (2020). Metodologia da Pesquisa. Editora Universitaria.

Santos, C. D., & Lima, G. H. (2021). Metodos Mistos. Revista de Educacao, 15(3), 123-145.
"""
    
    test_file = Path("test_apa.md")
    test_file.write_text(test_content, encoding='utf-8')
    
    # Valida o arquivo
    result = apa.validate_document(str(test_file))
    
    print(f"Arquivo: {result.file_path}")
    print(f"Pontuacao: {result.score:.1f}/100")
    print(f"Status: {'[CONFORME]' if result.is_compliant else '[NAO CONFORME]'}")
    print(f"Secoes encontradas: {len(result.sections_found)}/{len(apa.pf_sections)}")
    print(f"Citacoes: {result.citations_count}")
    print(f"Referencias: {result.references_count}")
    
    if result.issues:
        print("\nProblemas:")
        for issue in result.issues:
            print(f"  - {issue}")
    
    if result.warnings:
        print("\nAlertas:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    # Remove arquivo de teste
    test_file.unlink()


def test_apa_report():
    """Testa geracao de relatorio APA"""
    print("\n[TESTE] Relatorio APA")
    print("-" * 50)
    
    apa = APAIntegration()
    
    # Cria um arquivo de teste
    test_content = """# Introducao

Documento de teste.

## Referencias

Silva, A. B. (2020). Metodologia. Editora.
"""
    
    test_file = Path("test_apa_report.md")
    test_file.write_text(test_content, encoding='utf-8')
    
    # Gera relatorio
    result = apa.validate_document(str(test_file))
    report = apa.generate_apa_report(result)
    
    print(report)
    
    # Remove arquivo de teste
    test_file.unlink()


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DE INTEGRACAO APA")
    print("=" * 60)
    
    try:
        test_citation_validation()
        test_citation_formatting()
        test_reference_formatting()
        test_document_validation()
        test_apa_report()
        
        print("\n" + "=" * 60)
        print("[SUCESSO] TODOS OS TESTES EXECUTADOS COM SUCESSO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERRO] ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()