"""
Extração e conversão de referências bibliográficas para formato BibTeX.
Detecta referências em formato ABNT, APA, IEEE, Vancouver e outros.
"""

import re
from typing import List, Tuple


class ReferenceParser:
    """Extrai referências de texto de PDF e converte para BibTeX."""

    # Padrão para detectar seção de referências
    REFERENCE_SECTION_PATTERN = re.compile(
        r'(?:REFERENCES|REFERÊNCIAS|BIBLIOGRAPHY|BIBLIOGRAFIA|'
        r'WORKS\s+CITED|LITERATURA\s+CITADA|REFERENCIAS)',
        re.IGNORECASE
    )

    # Padrões de entrada de referência
    REFERENCE_PATTERNS = [
        # [1] Autor, Título, ...
        re.compile(r'^\[(\d+)\]\s+(.+?)(?:\.\s*$|$)', re.MULTILINE),
        # 1. Autor. Título...
        re.compile(r'^(\d+)\.\s+([A-Z][^.]*(?:\.\s*$|$))', re.MULTILINE),
        # SOBRENOME, Nome; SOBRENOME, Nome. Título...
        re.compile(r'^([A-ZÀ-Ú][A-ZÀ-Ú\s]+,\s*[A-Z][a-z]+.*?\.\s+.+?\.(?:\s|$))', re.MULTILINE),
    ]

    # Padrões para extrair campos de referências ABNT/APA
    AUTHOR_PATTERN = re.compile(r'^([A-ZÀ-Ú][A-ZÀ-Ú\s,]+?)\.\s+(.+?)(?:\.\s+|\.$)')
    YEAR_PATTERN = re.compile(r'\((\d{4})\)')
    TITLE_PATTERN = re.compile(r'[.!?]\s*([A-Z][^.!?]*(?:\.\s*$|$))')

    def __init__(self, text: str):
        self.text = text

    def parse(self) -> List[Tuple[str, str]]:
        """
        Extrai referências do texto e gera entradas BibTeX.
        Retorna: [(cite_key, bibtex_entry), ...]
        """
        references = []

        # 1. Localizar seção de referências
        ref_section = self._locate_reference_section()
        if not ref_section:
            # Tentar ABNT: últimas páginas geralmente têm as referências
            ref_section = self._extract_last_section()

        if not ref_section:
            return references

        # 2. Extrair entradas individuais
        entries = self._extract_entries(ref_section)

        # 3. Converter para BibTeX
        for i, entry in enumerate(entries):
            bib_entry = self._to_bibtex(entry, i + 1)
            if bib_entry:
                references.append(bib_entry)

        return references

    def _locate_reference_section(self) -> str:
        """Localiza a seção de referências no texto."""
        lines = self.text.split('\n')
        ref_start = -1

        for i, line in enumerate(lines):
            if self.REFERENCE_SECTION_PATTERN.search(line.strip().upper()):
                ref_start = i
                break

        if ref_start >= 0:
            # Pega da seção de referências até o final
            return '\n'.join(lines[ref_start:])
        return ""

    def _extract_last_section(self) -> str:
        """Extrai as últimas 30% linhas do texto (onde ficam as referências)."""
        lines = self.text.split('\n')
        if len(lines) < 50:
            return ""
        last_part = lines[len(lines) * 7 // 10:]
        return '\n'.join(last_part)

    def _extract_entries(self, text: str) -> List[str]:
        """Extrai entradas individuais de referência."""
        entries = []

        # Tentar cada padrão
        for pattern in self.REFERENCE_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                entries = [m[1] if isinstance(m, tuple) else m for m in matches]
                if len(entries) > 2:  # Pelo menos 2 referências encontradas
                    break

        # Fallback: dividir por linhas numeradas
        if not entries:
            lines = text.split('\n')
            current_entry = ""
            for line in lines:
                line = line.strip()
                if re.match(r'^\d+[\.\]]', line) or re.match(r'^\[?\d+\]?', line):
                    if current_entry:
                        entries.append(current_entry.strip())
                    current_entry = line
                elif line and current_entry:
                    current_entry += " " + line
            if current_entry:
                entries.append(current_entry.strip())

        return entries

    def _to_bibtex(self, entry: str, index: int) -> Tuple[str, str]:
        """Converte uma referência textual para BibTeX."""
        # Limpar
        entry = re.sub(r'^\[?\d+\]?\s*', '', entry).strip()

        # Extrair autor
        author = "Desconhecido"
        author_match = self.AUTHOR_PATTERN.search(entry)
        if author_match:
            author = author_match.group(1).strip().rstrip('.').strip()

        # Extrair ano
        year = "s.d."
        year_match = self.YEAR_PATTERN.search(entry)
        if year_match:
            year = year_match.group(1)

        # Extrair título
        title = entry
        title_match = self.TITLE_PATTERN.search(entry)
        if title_match:
            title = title_match.group(1)

        # Limpar título
        title = re.sub(r'\s+', ' ', title).strip().rstrip('.')

        # Gerar cite key
        first_author = author.split(',')[0].strip()
        first_author = re.sub(r'[^A-Za-zÀ-ú]', '', first_author)
        cite_key = f"{first_author}{year}" if year != "s.d." else f"{first_author}{index}"

        # Identificar tipo de publicação
        pub_type = self._guess_publication_type(entry)

        # Gerar entrada BibTeX
        bibtex = f"@{pub_type}{{{cite_key},\n"
        bibtex += f"  author = {{{author}}},\n"
        bibtex += f"  title = {{{title}}},\n"
        bibtex += f"  year = {{{year}}},\n"

        if pub_type in ["article", "inproceedings"]:
            journal_match = re.search(r'(?:Journal|Revista|Proceedings of|In:)\s+([^.(]+)', entry)
            if journal_match:
                bibtex += f"  journal = {{{journal_match.group(1).strip()}}},\n"

        if pub_type == "book":
            publisher_match = re.search(r'(?:Editora|Publisher|Press|Ed\.)\s*:\s*([^,]+)', entry)
            if publisher_match:
                bibtex += f"  publisher = {{{publisher_match.group(1).strip()}}},\n"

        bibtex += "}\n"

        return (cite_key, bibtex)

    def _guess_publication_type(self, entry: str) -> str:
        """Tenta adivinhar o tipo da publicação."""
        entry_upper = entry.upper()

        # Detectar padrões
        if re.search(r'(?:In:|Proceedings|Conference|Congress|Simpósio|Symposium)', entry_upper):
            return "inproceedings"
        elif re.search(r'(?:Journal|Revista|Review|Annals|Acta|Letters|Transactions)', entry_upper):
            return "article"
        elif re.search(r'(?:Editora|Publisher|Press|PhD|Doctoral|Master|Tese|Dissertação|Dissertacao)', entry_upper):
            return "phdthesis" if re.search(r'(?:PhD|Doctoral|Tese)', entry_upper) else "mastersthesis"
        elif re.search(r'(?:Technical Report|Relatório|Relatorio)', entry_upper):
            return "techreport"
        else:
            return "book"
