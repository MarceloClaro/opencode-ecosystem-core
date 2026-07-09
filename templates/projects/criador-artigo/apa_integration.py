#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APA Integration Module v1.0
Módulo de integração das normas APA 7ª edição com o ecossistema OpenCode.

Uso:
    from apa_integration import APAIntegration
    
    apa = APAIntegration()
    
    # Validar documento
    result = apa.validate_document("artigo.md")
    
    # Formatar citação
    citation = apa.format_citation("narrative", ["Silva"], "2020", "Pesquisa qualitativa")
    
    # Formatar referência
    reference = apa.format_reference("book", 
        authors=["Silva, A. B."], 
        year="2020", 
        title="Metodologia da Pesquisa"
    )
    
    # Verificar conformidade com PF
    pf_check = apa.check_pf_compliance("memoria.md")
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class APAConfig:
    """Configurações APA 7ª edição"""
    margins_cm: float = 2.54
    line_spacing: str = "double"
    font: str = "Times New Roman"
    font_size: int = 12
    alignment: str = "justified"
    paragraph_indent_cm: float = 1.27
    hanging_indent_cm: float = 1.27
    max_line_length: int = 65


@dataclass
class CitationResult:
    """Resultado de validação de citação"""
    citation: str
    is_valid: bool
    citation_type: str  # narrative, parenthetical, long
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ReferenceResult:
    """Resultado de validação de referência"""
    reference: str
    is_valid: bool
    ref_type: str  # book, article, website, etc.
    issues: List[str] = field(default_factory=list)
    formatted: str = ""


@dataclass
class DocumentValidation:
    """Resultado de validação de documento"""
    file_path: str
    is_compliant: bool
    score: float
    sections_found: List[str]
    sections_missing: List[str]
    citations_count: int
    references_count: int
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class APAIntegration:
    """Classe principal de integração APA"""
    
    def __init__(self, config: Optional[APAConfig] = None):
        self.config = config or APAConfig()
        self._load_patterns()
    
    def _load_patterns(self):
        """Carrega padroes regex para validacao"""
        # Padroes de citacao
        self.citation_patterns = {
            'narrative': r'[A-ZÀ-Ú][a-zà-ú]+(?:\s(?:&|e|et\sal\.)\s[A-ZÀ-Ú][a-zà-ú]+)*\s\(\d{4}[a-z]?\)',
            'parenthetical': r'\([A-ZÀ-Ú][a-zà-ú]+(?:\s(?:&|e|et\sal\.)\s[A-ZÀ-Ú][a-zà-ú]+)*,\s\d{4}[a-z]?\)',
            'long': r'^\s{4,}[A-ZÀ-Ú].*?\(\d{4}[a-z]?\).*?$',
        }
        
        # Padrao de referencia
        self.reference_pattern = r'^[A-ZÀ-Ú][a-zà-ú]+,\s[A-ZÀ-Ú]\.\s(?:[A-ZÀ-Ú]\.\s)?\(\d{4}[a-z]?\)\.\s.+'
        
        # Estrutura obrigatoria do PF
        self.pf_sections = [
            'Introdução',
            'Marco Teórico',
            'Metodologia',
            'Resultados',
            'Discussão',
            'Conclusões',
            'Referências'
        ]
        
        # Secoes opcionais do PF
        self.pf_optional_sections = [
            'Resumo',
            'Abstract',
            'Lista de Tabelas',
            'Lista de Figuras',
            'Sumário',
            'Índice'
        ]
    
    # ─── Validação de Citações ─────────────────────────────────────
    
    def validate_citation(self, citation: str) -> CitationResult:
        """Valida uma unica citacao"""
        citation = citation.strip()
        issues = []
        suggestions = []
        
        # Detecta tipo de citacao
        citation_type = "unknown"
        is_valid = False
        
        # Verifica citacao numerica (nao-APA)
        if re.match(r'^\[\d+\]$', citation) or re.match(r'^\[\d+(?:,\s*\d+)*\]$', citation):
            citation_type = "numeric"
            is_valid = False
            issues.append("Citacao numerica detectada - nao e formato APA")
            suggestions.append("Use formato: (Autor, Ano) ou (Autor1 & Autor2, Ano)")
        
        # Verifica citacao narrativa (Autor (Ano))
        elif re.match(r'^[A-ZÀ-Ú][a-zà-ú]+(?:\s(?:&|e|et\sal\.)\s[A-ZÀ-Ú][a-zà-ú]+)*\s\(\d{4}[a-z]?\)$', citation):
            citation_type = "narrative"
            is_valid = True
        
        # Verifica citacao com et al. narrativa
        elif re.match(r'^[A-ZÀ-Ú][a-zà-ú]+\s+et\sal\.\s\(\d{4}[a-z]?\)$', citation):
            citation_type = "narrative"
            is_valid = True
        
        # Verifica citacao parentetica ((Autor, Ano))
        elif re.match(r'^\([A-ZÀ-Ú][a-zà-ú]+(?:\s(?:&|e|et\sal\.)\s[A-ZÀ-Ú][a-zà-ú]+)*,\s\d{4}[a-z]?\)$', citation):
            citation_type = "parenthetical"
            is_valid = True
        
        # Verifica citacao com et al. parentetica
        elif re.match(r'^\([A-ZÀ-Ú][a-zà-ú]+\s+et\sal\.,\s\d{4}[a-z]?\)$', citation):
            citation_type = "parenthetical"
            is_valid = True
        
        # Verifica citacao longa
        elif re.match(self.citation_patterns['long'], citation, re.MULTILINE):
            citation_type = "long"
            is_valid = True
        
        # Verifica citacao com "et al." incorreto
        elif "et al" in citation.lower():
            citation_type = "et_al"
            is_valid = False
            issues.append("Uso incorreto de 'et al.'")
            suggestions.append("Use: (Autor et al., Ano) para 3+ autores")
        
        else:
            issues.append("Formato de citacao nao reconhecido")
            suggestions.append("Use formato APA: (Autor, Ano) ou Autor (Ano)")
        
        # Verifica ano
        year_match = re.search(r'\((\d{4}[a-z]?)\)', citation)
        if year_match:
            year = year_match.group(1)
            current_year = datetime.now().year
            if not year.isdigit() or int(year) > current_year + 1:
                issues.append(f"Ano invalido: {year}")
        
        return CitationResult(
            citation=citation,
            is_valid=is_valid,
            citation_type=citation_type,
            issues=issues,
            suggestions=suggestions
        )
    
    def validate_citations_in_text(self, text: str) -> Dict:
        """Valida todas as citações em um texto"""
        results = {
            'total_citations': 0,
            'valid_citations': 0,
            'invalid_citations': 0,
            'citations': [],
            'issues': [],
            'summary': {}
        }
        
        # Encontra todas as citações parentéticas
        parenthetical = re.findall(r'\([^)]*\d{4}[^)]*\)', text)
        
        # Encontra citações narrativas (simplificado)
        narrative = re.findall(r'[A-ZÀ-Ú][a-zà-ú]+(?:\s&\s[A-ZÀ-Ú][a-zà-ú]+)*\s\(\d{4}[a-z]?\)', text)
        
        all_citations = list(set(parenthetical + narrative))
        results['total_citations'] = len(all_citations)
        
        for citation in all_citations:
            validation = self.validate_citation(citation)
            results['citations'].append({
                'citation': citation,
                'is_valid': validation.is_valid,
                'type': validation.citation_type,
                'issues': validation.issues
            })
            
            if validation.is_valid:
                results['valid_citations'] += 1
            else:
                results['invalid_citations'] += 1
                results['issues'].extend(validation.issues)
        
        # Resumo
        results['summary'] = {
            'total': results['total_citations'],
            'valid': results['valid_citations'],
            'invalid': results['invalid_citations'],
            'compliance_rate': (results['valid_citations'] / results['total_citations'] * 100) 
                              if results['total_citations'] > 0 else 0
        }
        
        return results
    
    # ─── Formatação de Citações ─────────────────────────────────────
    
    def format_citation(self, citation_type: str, authors: List[str], year: str, 
                       title: str = "", page: str = "") -> str:
        """Formata uma citação no formato APA"""
        
        # Processa autores
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        elif len(authors) >= 3:
            author_str = f"{authors[0]} et al."
        else:
            author_str = "Autor Desconhecido"
        
        # Formata conforme tipo
        if citation_type == "narrative":
            if page:
                return f"{author_str} ({year}, p. {page})"
            return f"{author_str} ({year})"
        
        elif citation_type == "parenthetical":
            if page:
                return f"({author_str}, {year}, p. {page})"
            return f"({author_str}, {year})"
        
        elif citation_type == "long":
            # Citação longa (40+ palavras)
            indent = " " * int(self.config.paragraph_indent_cm * 2)  # Aproximadamente 5 espaços
            if page:
                return f"{indent}{title}\n{indent}(Autor, {year}, p. {page})"
            return f"{indent}{title}\n{indent}(Autor, {year})"
        
        return f"({author_str}, {year})"
    
    # ─── Formatação de Referências ─────────────────────────────────────
    
    def format_reference(self, ref_type: str, **kwargs) -> str:
        """Formata uma referência no formato APA"""
        
        authors = kwargs.get('authors', ['Autor Desconhecido'])
        year = kwargs.get('year', str(datetime.now().year))
        
        # Formata autores
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]}, & {authors[1]}"
        elif len(authors) >= 3:
            author_str = f"{authors[0]}, et al."
        else:
            author_str = "Autor Desconhecido"
        
        # Formata conforme tipo
        if ref_type == "book":
            title = kwargs.get('title', 'Título não informado')
            publisher = kwargs.get('publisher', 'Editora não informada')
            return f"{author_str} ({year}). *{title}*. {publisher}."
        
        elif ref_type == "article":
            title = kwargs.get('title', 'Título não informado')
            journal = kwargs.get('journal', 'Periódico não informado')
            volume = kwargs.get('volume', '')
            issue = kwargs.get('issue', '')
            pages = kwargs.get('pages', '')
            doi = kwargs.get('doi', '')
            
            ref = f"{author_str} ({year}). *{title}*. {journal}"
            if volume:
                ref += f", *{volume}*"
            if issue:
                ref += f"({issue})"
            if pages:
                ref += f", {pages}"
            ref += "."
            if doi:
                ref += f" https://doi.org/{doi}"
            return ref
        
        elif ref_type == "website":
            title = kwargs.get('title', 'Título não informado')
            url = kwargs.get('url', '')
            return f"{author_str} ({year}). *{title}*. {url}"
        
        elif ref_type == "chapter":
            title = kwargs.get('title', 'Título do capítulo')
            book_title = kwargs.get('book_title', 'Título do livro')
            editors = kwargs.get('editors', [])
            pages = kwargs.get('pages', '')
            publisher = kwargs.get('publisher', 'Editora não informada')
            
            editor_str = "Ed." if len(editors) == 1 else "Eds."
            editors_formatted = ", ".join(editors) if editors else "Editor"
            
            ref = f"{author_str} ({year}). {title}. Em {editors_formatted} ({editor_str}), *{book_title}*"
            if pages:
                ref += f" (pp. {pages})"
            ref += f". {publisher}."
            return ref
        
        elif ref_type == "thesis":
            title = kwargs.get('title', 'Título não informado')
            institution = kwargs.get('institution', 'Instituição não informada')
            thesis_type = kwargs.get('thesis_type', 'Tese')
            return f"{author_str} ({year}). *{title}* [{thesis_type}, {institution}]."
        
        return f"{author_str} ({year}). Referência não formatada."
    
    # ─── Validação de Documentos ─────────────────────────────────────
    
    def validate_document(self, file_path: str) -> DocumentValidation:
        """Valida um documento completo quanto à conformidade APA"""
        
        path = Path(file_path)
        if not path.exists():
            return DocumentValidation(
                file_path=file_path,
                is_compliant=False,
                score=0,
                sections_found=[],
                sections_missing=self.pf_sections,
                citations_count=0,
                references_count=0,
                issues=[f"Arquivo não encontrado: {file_path}"],
                warnings=[],
                suggestions=[]
            )
        
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            return DocumentValidation(
                file_path=file_path,
                is_compliant=False,
                score=0,
                sections_found=[],
                sections_missing=self.pf_sections,
                citations_count=0,
                references_count=0,
                issues=[f"Erro ao ler arquivo: {str(e)}"],
                warnings=[],
                suggestions=[]
            )
        
        # Valida seções
        sections_found = []
        sections_missing = []
        
        for section in self.pf_sections:
            if re.search(rf'#+\s*{section}', content, re.IGNORECASE):
                sections_found.append(section)
            else:
                sections_missing.append(section)
        
        # Valida citações
        citations_result = self.validate_citations_in_text(content)
        
        # Valida referências
        references_result = self._validate_references(content)
        
        # Calcula pontuação
        score = self._calculate_compliance_score(
            sections_found, 
            sections_missing,
            citations_result['summary']['compliance_rate'],
            references_result['compliance_rate']
        )
        
        # Coleta issues e warnings
        issues = []
        warnings = []
        suggestions = []
        
        # Issues de seções
        if sections_missing:
            issues.append(f"Seções obrigatórias ausentes: {', '.join(sections_missing)}")
        
        # Issues de citações
        if citations_result['invalid_citations'] > 0:
            issues.append(f"{citations_result['invalid_citations']} citações inválidas encontradas")
        
        # Warnings
        if citations_result['total_citations'] < 10:
            warnings.append(f"Poucas citações encontradas: {citations_result['total_citations']}")
        
        if references_result['total'] < 15:
            warnings.append(f"Poucas referências encontradas: {references_result['total']}")
        
        # Suggestions
        suggestions.extend(references_result.get('suggestions', []))
        
        return DocumentValidation(
            file_path=file_path,
            is_compliant=score >= 80,
            score=score,
            sections_found=sections_found,
            sections_missing=sections_missing,
            citations_count=citations_result['total_citations'],
            references_count=references_result['total'],
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_references(self, content: str) -> Dict:
        """Valida seção de referências"""
        result = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'compliance_rate': 0,
            'suggestions': []
        }
        
        # Procura por seção de referências
        ref_section = re.search(
            r'#+\s*(Referências|References|Bibliografia)\s*\n(.*?)(?=\n#|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if not ref_section:
            result['suggestions'].append("Adicionar seção 'Referências' ao final do documento")
            return result
        
        ref_content = ref_section.group(2)
        references = [
            line.strip() 
            for line in ref_content.split('\n') 
            if line.strip() and not line.strip().startswith('#')
        ]
        
        result['total'] = len(references)
        
        for ref in references:
            if re.match(self.reference_pattern, ref):
                result['valid'] += 1
            else:
                result['invalid'] += 1
        
        if result['total'] > 0:
            result['compliance_rate'] = (result['valid'] / result['total']) * 100
        
        # Verifica ordenação alfabética
        if references:
            sorted_refs = sorted(references, key=lambda x: x.split(',')[0].lower())
            if references != sorted_refs:
                result['suggestions'].append("Referências não estão em ordem alfabética")
        
        return result
    
    def _calculate_compliance_score(self, sections_found: List[str], sections_missing: List[str],
                                   citations_compliance: float, references_compliance: float) -> float:
        """Calcula pontuação de conformidade"""
        score = 0
        
        # Seções (40 pontos)
        if self.pf_sections:
            section_score = (len(sections_found) / len(self.pf_sections)) * 40
            score += section_score
        
        # Citações (30 pontos)
        score += (citations_compliance / 100) * 30
        
        # Referências (30 pontos)
        score += (references_compliance / 100) * 30
        
        return min(100.0, score)
    
    # ─── Integração com Pipeline ─────────────────────────────────────
    
    def validate_maswos_output(self, output_dir: str) -> Dict:
        """Valida output do pipeline MASWOS"""
        output_path = Path(output_dir)
        
        if not output_path.exists():
            return {'status': 'error', 'message': 'Diretório não encontrado'}
        
        results = {
            'status': 'completed',
            'files_validated': 0,
            'total_score': 0,
            'files': []
        }
        
        # Valida todos os arquivos .md
        for md_file in output_path.glob("*.md"):
            if md_file.name in ['SKILL.md', 'README.md']:
                continue
            
            validation = self.validate_document(str(md_file))
            results['files'].append({
                'file': md_file.name,
                'score': validation.score,
                'is_compliant': validation.is_compliant,
                'issues': validation.issues,
                'warnings': validation.warnings
            })
            results['files_validated'] += 1
            results['total_score'] += validation.score
        
        if results['files_validated'] > 0:
            results['total_score'] /= results['files_validated']
        
        return results
    
    def integrate_with_correction_loop(self, manuscript_dir: str) -> Dict:
        """Integra com o correction_loop.py"""
        manuscript_path = Path(manuscript_dir)
        
        # Valida documento
        validation = self.validate_document(str(manuscript_path))
        
        # Gera ações de correção baseadas na validação
        actions = []
        
        if validation.issues:
            for issue in validation.issues:
                if "seção" in issue.lower():
                    actions.append("ADD_MISSING_SECTIONS")
                elif "citação" in issue.lower():
                    actions.append("FIX_CITATIONS")
                elif "referência" in issue.lower():
                    actions.append("FIX_REFERENCES")
        
        return {
            'validation': validation,
            'actions': actions,
            'integration_status': 'ready'
        }
    
    def generate_apa_report(self, validation: DocumentValidation) -> str:
        """Gera relatório de conformidade APA"""
        report = []
        report.append("=" * 60)
        report.append("RELATORIO DE CONFORMIDADE APA 7a EDICAO")
        report.append("=" * 60)
        report.append(f"Arquivo: {validation.file_path}")
        report.append(f"Pontuacao: {validation.score:.1f}/100")
        report.append(f"Status: {'[CONFORME]' if validation.is_compliant else '[NAO CONFORME]'}")
        report.append("")
        
        # Seções
        report.append("SECOES:")
        report.append(f"  Encontradas: {len(validation.sections_found)}/{len(self.pf_sections)}")
        if validation.sections_found:
            for s in validation.sections_found:
                report.append(f"    [OK] {s}")
        if validation.sections_missing:
            for s in validation.sections_missing:
                report.append(f"    [FALTA] {s}")
        report.append("")
        
        # Citações e Referências
        report.append("CITACOES E REFERENCIAS:")
        report.append(f"  Citacoes encontradas: {validation.citations_count}")
        report.append(f"  Referencias encontradas: {validation.references_count}")
        report.append("")
        
        # Issues
        if validation.issues:
            report.append("PROBLEMAS:")
            for issue in validation.issues:
                report.append(f"  - {issue}")
            report.append("")
        
        # Warnings
        if validation.warnings:
            report.append("ALERTAS:")
            for warning in validation.warnings:
                report.append(f"  - {warning}")
            report.append("")
        
        # Suggestions
        if validation.suggestions:
            report.append("SUGESTOES:")
            for suggestion in validation.suggestions:
                report.append(f"  - {suggestion}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Função principal para uso via CLI"""
    if len(sys.argv) < 2:
        print("Uso: python apa_integration.py <comando> <arquivo>")
        print("Comandos:")
        print("  validate <arquivo.md>     - Valida documento APA")
        print("  citations <arquivo.md>    - Valida citações")
        print("  references <arquivo.md>   - Valida referências")
        print("  report <arquivo.md>       - Gera relatório completo")
        return
    
    cmd = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    apa = APAIntegration()
    
    if cmd == "validate":
        result = apa.validate_document(file_path)
        print(f"Pontuação: {result.score:.1f}/100")
        print(f"Status: {'CONFORME' if result.is_compliant else 'NÃO CONFORME'}")
        
    elif cmd == "citations":
        content = Path(file_path).read_text(encoding='utf-8')
        result = apa.validate_citations_in_text(content)
        print(f"Total: {result['summary']['total']}")
        print(f"Válidas: {result['summary']['valid']}")
        print(f"Inválidas: {result['summary']['invalid']}")
        print(f"Conformidade: {result['summary']['compliance_rate']:.1f}%")
        
    elif cmd == "references":
        content = Path(file_path).read_text(encoding='utf-8')
        result = apa._validate_references(content)
        print(f"Total: {result['total']}")
        print(f"Válidas: {result['valid']}")
        print(f"Conformidade: {result['compliance_rate']:.1f}%")
        
    elif cmd == "report":
        result = apa.validate_document(file_path)
        report = apa.generate_apa_report(result)
        print(report)
        
    else:
        print(f"Comando desconhecido: {cmd}")


if __name__ == "__main__":
    main()