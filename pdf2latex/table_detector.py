"""
Detecção e conversão de tabelas de PDFs para LaTeX tabular/longtable.
Usa camelot-py e pdfplumber como backends.
"""

import re
from pathlib import Path
from typing import List, Tuple


class TableDetector:
    """Detecta e converte tabelas de PDFs para código LaTeX."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path

    def detect(self) -> List[Tuple[str, str, int]]:
        """
        Detecta tabelas no PDF e converte para LaTeX.
        Retorna: [(codigo_latex_tabular, legenda, numero_pagina), ...]
        """
        tables = []

        # Método 1: Camelot (melhor para tabelas com bordas)
        try:
            tables += self._detect_with_camelot()
        except Exception:
            pass

        # Método 2: pdfplumber (fallback)
        if not tables:
            try:
                tables += self._detect_with_pdfplumber()
            except Exception:
                pass

        return tables

    def _detect_with_camelot(self) -> List[Tuple]:
        """Usa Camelot para detectar tabelas."""
        import camelot

        tables_latex = []
        try:
            # Tenta modo lattice (bordas) primeiro
            tables = camelot.read_pdf(str(self.pdf_path), pages="all", flavor="lattice")
            if len(tables) == 0:
                # Fallback para stream (sem bordas)
                tables = camelot.read_pdf(str(self.pdf_path), pages="all", flavor="stream")

            for i, table in enumerate(tables):
                if table.shape[0] > 1:  # Ignorar tabelas de 1 linha
                    latex_code = self._dataframe_to_latex(table.df)
                    legenda = f"Tabela_{i+1}_pag_{table.parsing_report.get('page', '?')}"
                    pagina = table.parsing_report.get("page", 0)
                    tables_latex.append((latex_code, legenda, pagina))

        except Exception:
            pass

        return tables_latex

    def _dataframe_to_latex(self, df) -> str:
        """Converte DataFrame pandas para código LaTeX tabular."""
        num_cols = len(df.columns)
        col_format = "|" + "|".join(["c"] * num_cols) + "|"

        lines = []
        lines.append(r"\begin{table}[h]")
        lines.append(r"\centering")
        lines.append(r"\caption{Tabela extraída do PDF}")
        lines.append(r"\label{tab:extraida}")
        lines.append(r"\begin{tabular}{" + col_format + "}")
        lines.append(r"\hline")

        for i, row in df.iterrows():
            row_str = " & ".join(str(val).strip().replace("&", r"\&") for val in row)
            row_str += r" \\"
            if i == 0:
                row_str += " \\hline"
            elif i < len(df) - 1:
                row_str += ""
            lines.append(row_str)

        lines.append(r"\hline")
        lines.append(r"\end{tabular}")
        lines.append(r"\end{table}")

        return "\n".join(lines)

    def _detect_with_pdfplumber(self) -> List[Tuple]:
        """Usa pdfplumber como fallback para detecção de tabelas."""
        import pdfplumber

        tables_latex = []

        with pdfplumber.open(str(self.pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                for i, table in enumerate(tables):
                    if len(table) > 1:
                        num_cols = max(len(row) for row in table)
                        col_format = "|" + "|".join(["c"] * num_cols) + "|"

                        lines = []
                        lines.append(r"\begin{table}[h]")
                        lines.append(r"\centering")
                        lines.append(r"\caption{Tabela extraída (pág. " + str(page_num) + ")}")
                        lines.append(r"\label{tab:extraida_p" + str(page_num) + "}")
                        lines.append(r"\begin{tabular}{" + col_format + "}")
                        lines.append(r"\hline")

                        for j, row in enumerate(table):
                            row_data = [str(cell or "").strip() for cell in row]
                            row_str = " & ".join(
                                d.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
                                for d in row_data
                            )
                            row_str += r" \\"
                            if j == 0:
                                row_str += " \\hline"
                            lines.append(row_str)

                        lines.append(r"\hline")
                        lines.append(r"\end{tabular}")
                        lines.append(r"\end{table}")

                        tables_latex.append(("\n".join(lines), f"Tabela_p{page_num}_{i+1}", page_num))

        return tables_latex
