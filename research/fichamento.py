# -*- coding: utf-8 -*-
"""
Fichamentos e Resenhas Críticas (SPEC-017)
===========================================
Gera, para cada artigo baixado e convertido em Markdown:

1. **Fichamento** (`pesquisa/fichamentos/`) — em formato ABNT atualizado
   (NBR 6023:2018 para referências; NBR 10520:2023 para citações),
   contendo três camadas clássicas:
   - Fichamento bibliográfico (resumo objetivo)
   - Fichamento de citação (trechos literais relevantes)
   - Fichamento crítico (análise vinculada ao tema de pesquisa)

2. **Resenha crítica** (`pesquisa/resenhas/`) — texto corrido, com
   criticidade explícita ao tema de pesquisa: aderência, contribuições,
   limitações metodológicas, lacunas e diálogo com a literatura.

3. **Referências** em ABNT e APA 7ª edição, consolidadas em
   `referencias_abnt.md`, `referencias_apa.md` e `referencias.bib`.

Caminho padrão é 100% determinístico (heurísticas stdlib). Se a variável
de ambiente OPENAI_API_KEY estiver disponível, a resenha pode ser
enriquecida por LLM (opcional, nunca obrigatório).
"""

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .searchers import PaperRecord

logger = logging.getLogger("research.fichamento")

# palavras funcionais PT/EN ignoradas no cálculo de aderência ao tema
_STOPWORDS = {
    "a", "o", "e", "de", "da", "do", "das", "dos", "em", "para", "com", "um",
    "uma", "no", "na", "que", "por", "os", "as", "ao", "à", "se", "é",
    "the", "of", "and", "in", "to", "for", "on", "with", "a", "an", "is",
    "are", "by", "as", "at", "from", "this", "that", "we", "our", "be",
}


def _tokens(text: str) -> set:
    words = re.findall(r"[\wÀ-ÿ]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


# ======================================================================
# Formatação de referências — ABNT NBR 6023:2018 e APA 7
# ======================================================================
class CitationFormatter:
    """Formata referências em ABNT (NBR 6023:2018) e APA 7ª edição."""

    # ------------------------------------------------------------------
    @staticmethod
    def _split_name(full: str) -> Tuple[str, str]:
        """Retorna (sobrenome, resto). Trata 'Sobrenome, Nome' e 'Nome Sobrenome'."""
        full = full.strip()
        if "," in full:
            last, first = full.split(",", 1)
            return last.strip(), first.strip()
        parts = full.split()
        if len(parts) == 1:
            return parts[0], ""
        return parts[-1], " ".join(parts[:-1])

    # ------------------------------------------------------------------
    @classmethod
    def abnt(cls, rec: PaperRecord) -> str:
        """Referência ABNT NBR 6023:2018.
        Ex.: SILVA, J.; SANTOS, M. Título do artigo. Nome do Periódico, v. ?, 2023.
        DOI: https://doi.org/...
        """
        autores = []
        for a in rec.authors[:10]:
            if not a.strip():
                continue
            last, first = cls._split_name(a)
            initials = " ".join(f"{p[0].upper()}." for p in first.split() if p)
            autores.append(f"{last.upper()}, {initials}".rstrip(", "))
        if len(rec.authors) > 10:
            autores.append("et al.")
        autores_str = "; ".join(autores) if autores else "AUTOR DESCONHECIDO"

        ano = str(rec.year) if rec.year else "[s.d.]"
        titulo = rec.title.rstrip(".")
        venue = rec.venue or ("arXiv" if rec.arxiv_id else "[S.l.: s.n.]")
        ref = f"{autores_str} {titulo}. **{venue}**, {ano}."
        if rec.doi:
            ref += f" DOI: https://doi.org/{rec.doi}."
        elif rec.url:
            ref += f" Disponível em: {rec.url}. Acesso em: {cls._today_abnt()}."
        return ref

    @staticmethod
    def _today_abnt() -> str:
        import datetime
        meses = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.",
                 "jul.", "ago.", "set.", "out.", "nov.", "dez."]
        hoje = datetime.date.today()
        return f"{hoje.day} {meses[hoje.month - 1]} {hoje.year}"

    # ------------------------------------------------------------------
    @classmethod
    def apa(cls, rec: PaperRecord) -> str:
        """Referência APA 7ª edição.
        Ex.: Silva, J., & Santos, M. (2023). Título do artigo. Periódico. https://doi.org/...
        """
        autores = []
        for a in rec.authors[:20]:
            if not a.strip():
                continue
            last, first = cls._split_name(a)
            initials = " ".join(f"{p[0].upper()}." for p in first.split() if p)
            autores.append(f"{last}, {initials}".rstrip(", "))
        if len(autores) > 1:
            autores_str = ", ".join(autores[:-1]) + f", & {autores[-1]}"
        elif autores:
            autores_str = autores[0]
        else:
            autores_str = "Autor desconhecido"

        ano = str(rec.year) if rec.year else "n.d."
        titulo = rec.title.rstrip(".")
        venue = rec.venue or ("arXiv" if rec.arxiv_id else "")
        ref = f"{autores_str} ({ano}). {titulo}."
        if venue:
            ref += f" *{venue}*."
        if rec.doi:
            ref += f" https://doi.org/{rec.doi}"
        elif rec.url:
            ref += f" {rec.url}"
        return ref

    # ------------------------------------------------------------------
    @classmethod
    def abnt_citacao_direta(cls, rec: PaperRecord, pagina: str = "N") -> str:
        """Formato de citação NBR 10520:2023: (Sobrenome, ano, p. N)."""
        if rec.authors:
            last, _ = cls._split_name(rec.authors[0])
            autor = last.capitalize()
            if len(rec.authors) == 2:
                last2, _ = cls._split_name(rec.authors[1])
                autor = f"{autor}; {last2.capitalize()}"
            elif len(rec.authors) > 2:
                autor += " et al."
        else:
            autor = "Autor desconhecido"
        ano = rec.year or "s.d."
        return f"({autor}, {ano}, p. {pagina})"

    @classmethod
    def bibtex(cls, rec: PaperRecord, key: str) -> str:
        autores = " and ".join(rec.authors[:20]) or "Unknown"
        campos = [
            f"  author = {{{autores}}}",
            f"  title = {{{rec.title}}}",
        ]
        if rec.year:
            campos.append(f"  year = {{{rec.year}}}")
        if rec.venue:
            campos.append(f"  journal = {{{rec.venue}}}")
        if rec.doi:
            campos.append(f"  doi = {{{rec.doi}}}")
        if rec.url:
            campos.append(f"  url = {{{rec.url}}}")
        entry_type = "article" if (rec.doi or rec.venue) else "misc"
        return f"@{entry_type}{{{key},\n" + ",\n".join(campos) + "\n}"


# ======================================================================
# Análise crítica heurística (sempre disponível, stdlib)
# ======================================================================
@dataclass
class CriticalAnalysis:
    aderencia_score: float          # 0.0–10.0
    termos_compartilhados: List[str]
    pontos_fortes: List[str]
    limitacoes: List[str]
    lacunas: List[str]
    veredicto: str


class CriticalAnalyzer:
    """Analisa criticamente um artigo em relação ao tema de pesquisa."""

    def __init__(self, tema: str):
        self.tema = tema
        self.tema_tokens = _tokens(tema)

    # ------------------------------------------------------------------
    def analyze(self, rec: PaperRecord, fulltext: str = "") -> CriticalAnalysis:
        corpus = " ".join([rec.title, rec.abstract, fulltext[:20000]])
        corpus_tokens = _tokens(corpus)
        shared = sorted(self.tema_tokens & corpus_tokens)
        aderencia = round(
            10.0 * len(shared) / max(1, len(self.tema_tokens)), 1)
        aderencia = min(10.0, aderencia)

        fortes, limitacoes, lacunas = [], [], []
        texto_lower = (rec.abstract + " " + fulltext[:20000]).lower()

        # heurísticas de qualidade metodológica
        if rec.citations and rec.citations > 100:
            fortes.append(f"Alto impacto bibliométrico ({rec.citations} citações), "
                          "indicando reconhecimento consolidado pela comunidade.")
        if any(k in texto_lower for k in ("experiment", "empirical", "dataset",
                                          "benchmark", "avaliação experimental")):
            fortes.append("Fundamentação empírica com experimentos ou benchmarks, "
                          "favorecendo a verificabilidade dos resultados.")
        if any(k in texto_lower for k in ("open source", "github.com", "código",
                                          "reproducib", "replicab")):
            fortes.append("Preocupação explícita com reprodutibilidade ou "
                          "disponibilização de código, critério valorizado em "
                          "avaliações Qualis A1.")
        if any(k in texto_lower for k in ("survey", "review", "revisão")):
            fortes.append("Caráter de revisão/síntese, útil como porta de entrada "
                          "para o estado da arte do tema.")
        if not fortes:
            fortes.append("Contribuição conceitual pertinente ao campo, ainda que "
                          "sem sinais explícitos de validação empírica no resumo.")

        if not any(k in texto_lower for k in ("statistic", "p-value", "confidence",
                                              "estatístic", "significan")):
            limitacoes.append("Ausência de menção a validação estatística "
                              "(p-valores, intervalos de confiança, tamanhos de "
                              "efeito) no material analisado.")
        if not any(k in texto_lower for k in ("limitation", "limitaç", "threat")):
            limitacoes.append("O texto não declara limitações explícitas, o que "
                              "exige leitura cética das conclusões.")
        if rec.year and rec.year < 2020:
            limitacoes.append(f"Publicação de {rec.year}; resultados podem estar "
                              "defasados frente ao estado da arte atual.")
        if not limitacoes:
            limitacoes.append("Sem limitações evidentes detectáveis pela análise "
                              "automática; recomenda-se leitura integral.")

        if aderencia < 4.0:
            lacunas.append("Baixa sobreposição terminológica com o tema de "
                           "pesquisa; o artigo cobre o tema apenas de forma "
                           "tangencial e demanda triangulação com outras fontes.")
        else:
            lacunas.append("O artigo não esgota o tema; identificar se aborda as "
                           "variáveis específicas do problema de pesquisa antes "
                           "de citá-lo como evidência central.")

        if aderencia >= 7.0:
            veredicto = ("LEITURA PRIORITÁRIA — alta aderência ao tema; candidato "
                         "a referência central na revisão de literatura.")
        elif aderencia >= 4.0:
            veredicto = ("LEITURA RECOMENDADA — aderência moderada; útil como "
                         "referência de apoio ou contraste metodológico.")
        else:
            veredicto = ("LEITURA OPCIONAL — aderência baixa; manter no corpus "
                         "apenas se oferecer método ou dado transferível.")

        return CriticalAnalysis(
            aderencia_score=aderencia,
            termos_compartilhados=shared[:15],
            pontos_fortes=fortes,
            limitacoes=limitacoes,
            lacunas=lacunas,
            veredicto=veredicto,
        )


# ======================================================================
# Geradores de documentos
# ======================================================================
class FichamentoWriter:
    """Escreve fichamentos e resenhas críticas em Markdown ABNT/APA."""

    def __init__(self, fichamentos_dir: str, resenhas_dir: str, tema: str):
        self.fichamentos_dir = Path(fichamentos_dir)
        self.resenhas_dir = Path(resenhas_dir)
        self.fichamentos_dir.mkdir(parents=True, exist_ok=True)
        self.resenhas_dir.mkdir(parents=True, exist_ok=True)
        self.tema = tema
        self.analyzer = CriticalAnalyzer(tema)

    # ------------------------------------------------------------------
    @staticmethod
    def _extract_quotes(fulltext: str, max_quotes: int = 3) -> List[str]:
        """Seleciona trechos citáveis (frases informativas de 120–400 chars)."""
        if not fulltext:
            return []
        # remove frontmatter e linhas de ruído
        body = re.sub(r"^---.*?---\s*", "", fulltext, flags=re.DOTALL)
        sentences = re.split(r"(?<=[.!?])\s+", " ".join(body.split()))
        quotes = []
        for s in sentences:
            if 120 <= len(s) <= 400 and not s.startswith(("#", "|", "http")):
                low = s.lower()
                if any(k in low for k in ("we propose", "results show", "we find",
                                          "demonstrate", "conclu", "propomos",
                                          "resultados", "significant", "novel",
                                          "this paper", "este artigo", "we present")):
                    quotes.append(s.strip())
            if len(quotes) >= max_quotes:
                break
        if not quotes:  # fallback: primeiras frases longas
            quotes = [s.strip() for s in sentences
                      if 120 <= len(s) <= 400][:max_quotes]
        return quotes

    @staticmethod
    def _slug(rec: PaperRecord) -> str:
        slug = re.sub(r"[^\w\s-]", "", rec.title.lower()).strip()
        slug = re.sub(r"[-\s]+", "-", slug)[:60].rstrip("-")
        return f"{rec.year or 'sd'}-{slug or 'artigo'}"

    # ------------------------------------------------------------------
    def fichamento(self, rec: PaperRecord, fulltext: str = "",
                   md_path: str = "") -> str:
        """Gera o fichamento em três camadas (bibliográfico, citação, crítico)."""
        analysis = self.analyzer.analyze(rec, fulltext)
        quotes = self._extract_quotes(fulltext)
        cit = CitationFormatter

        resumo = rec.abstract or "Resumo não disponível nos metadados; consultar o texto integral em Markdown."
        if len(resumo) > 1500:
            resumo = resumo[:1500].rsplit(" ", 1)[0] + " [...]"

        linhas = [
            f"# Fichamento — {rec.title}",
            "",
            f"**Tema de pesquisa:** {self.tema}",
            f"**Aderência ao tema:** {analysis.aderencia_score}/10 — {analysis.veredicto}",
            "",
            "## 1. Referência",
            "",
            f"**ABNT (NBR 6023:2018):** {cit.abnt(rec)}",
            "",
            f"**APA (7ª ed.):** {cit.apa(rec)}",
            "",
            f"**Formato de citação no texto (NBR 10520:2023):** {cit.abnt_citacao_direta(rec)}",
            "",
            "## 2. Identificação",
            "",
            "| Campo | Valor |",
            "| --- | --- |",
            f"| Autores | {'; '.join(rec.authors[:10]) or 'não informado'} |",
            f"| Ano | {rec.year or 'não informado'} |",
            f"| Veículo | {rec.venue or 'não informado'} |",
            f"| DOI | {rec.doi or '—'} |",
            f"| Plataforma de origem | {rec.source} |",
            f"| Citações | {rec.citations if rec.citations is not None else '—'} |",
            f"| Texto integral (MD) | {Path(md_path).name if md_path else 'não convertido'} |",
            "",
            "## 3. Fichamento bibliográfico (resumo objetivo)",
            "",
            resumo,
            "",
            "## 4. Fichamento de citação (trechos literais)",
            "",
        ]
        if quotes:
            for q in quotes:
                linhas.append(f'> "{q}" {cit.abnt_citacao_direta(rec)}')
                linhas.append("")
        else:
            linhas.append("_Trechos citáveis não extraídos automaticamente; "
                          "consultar o Markdown do texto integral._")
            linhas.append("")

        linhas += [
            "## 5. Fichamento crítico (análise vinculada ao tema)",
            "",
            f"**Termos compartilhados com o tema:** "
            f"{', '.join(analysis.termos_compartilhados) or 'nenhum termo relevante em comum'}",
            "",
            "**Pontos fortes:**",
            "",
        ]
        linhas += [f"- {p}" for p in analysis.pontos_fortes]
        linhas += ["", "**Limitações e riscos de viés:**", ""]
        linhas += [f"- {l}" for l in analysis.limitacoes]
        linhas += ["", "**Lacunas em relação ao tema de pesquisa:**", ""]
        linhas += [f"- {l}" for l in analysis.lacunas]
        linhas += [
            "",
            "---",
            "_Fichamento gerado pelo subsistema research do opencode-ecosystem-core "
            "(ABNT NBR 6023:2018 / NBR 10520:2023 / APA 7)._",
        ]

        dest = self.fichamentos_dir / f"fichamento-{self._slug(rec)}.md"
        dest.write_text("\n".join(linhas), encoding="utf-8")
        return str(dest)

    # ------------------------------------------------------------------
    def resenha(self, rec: PaperRecord, fulltext: str = "") -> str:
        """Gera resenha crítica em texto corrido, com criticidade ao tema."""
        analysis = self.analyzer.analyze(rec, fulltext)
        cit = CitationFormatter
        autor_ano = cit.abnt_citacao_direta(rec).replace(", p. N", "")

        primeiro_autor = rec.authors[0].split(",")[0].split()[-1] if rec.authors else "o autor"

        p1 = (f"A obra em análise, intitulada \u201c{rec.title}\u201d, publicada em "
              f"{rec.year or 'data não informada'}"
              f"{' no veículo ' + rec.venue if rec.venue else ''}, foi selecionada "
              f"a partir da plataforma {rec.source} durante a revisão sistemática "
              f"do tema \u201c{self.tema}\u201d, e sua leitura foi avaliada com "
              f"aderência de {analysis.aderencia_score} em uma escala de zero a "
              f"dez, o que orienta o seu papel no corpus desta pesquisa.")

        resumo = rec.abstract[:800] if rec.abstract else ""
        p2 = (f"Em termos de conteúdo, {primeiro_autor} e colaboradores "
              f"{autor_ano} desenvolvem a seguinte proposta central: "
              f"{resumo or 'o resumo não está disponível nos metadados, de modo que a síntese deve ser conferida no texto integral convertido para Markdown na subpasta de pesquisa'}"
              f"{'...' if resumo and len(rec.abstract) > 800 else ''}")

        p3 = ("No que diz respeito às contribuições, destacam-se os seguintes "
              "aspectos: " + " ".join(analysis.pontos_fortes) +
              " Esses elementos justificam a permanência da obra no corpus, "
              "sobretudo pela possibilidade de diálogo com outras fontes "
              "levantadas nas demais plataformas.")

        p4 = ("Sob o olhar crítico, contudo, é preciso registrar ressalvas. " +
              " ".join(analysis.limitacoes) +
              " Tais limitações não invalidam a obra, mas delimitam o alcance "
              "das generalizações que dela podem ser extraídas para o tema "
              "investigado.")

        p5 = ("Quanto às lacunas em relação ao tema de pesquisa, observa-se que " +
              " ".join(analysis.lacunas) +
              f" Em síntese, o veredicto desta resenha é: {analysis.veredicto}")

        linhas = [
            f"# Resenha crítica — {rec.title}",
            "",
            f"**Tema de pesquisa:** {self.tema}",
            f"**Aderência:** {analysis.aderencia_score}/10",
            "",
            p1, "", p2, "", p3, "", p4, "", p5, "",
            "## Referência da obra resenhada",
            "",
            f"**ABNT:** {cit.abnt(rec)}",
            "",
            f"**APA 7:** {cit.apa(rec)}",
            "",
            "---",
            "_Resenha gerada pelo subsistema research do opencode-ecosystem-core; "
            "recomenda-se revisão humana antes de uso em manuscrito final._",
        ]
        dest = self.resenhas_dir / f"resenha-{self._slug(rec)}.md"
        dest.write_text("\n".join(linhas), encoding="utf-8")
        return str(dest)

    # ------------------------------------------------------------------
    def enrich_with_llm(self, rec: PaperRecord, fulltext: str,
                        resenha_path: str,
                        provider: str = "auto",
                        model: Optional[str] = None) -> bool:
        """Opcional: aprofunda a resenha via LLM local (Ollama) ou nuvem.

        Ordem de resolução (``provider='auto'``): Ollama local →
        API OpenAI-compatível → desativado (pipeline segue determinístico).
        Force um provedor com ``provider='ollama'``/``'openai'`` ou pela
        variável de ambiente ``RESEARCH_LLM``. O modelo local padrão é
        ``llama3.2`` (configurável via ``OLLAMA_MODEL`` ou ``model=``).
        """
        try:
            from .llm_client import LLMClient
            client = LLMClient(provider=provider, model=model)
            if not client.available():
                logger.debug("enriquecimento LLM indisponível: nenhum "
                             "provedor (Ollama/OpenAI) acessível")
                return False
            prompt = (
                f"Tema de pesquisa: {self.tema}\n\n"
                f"Artigo: {rec.title} ({rec.year})\n"
                f"Resumo: {rec.abstract[:1500]}\n\n"
                f"Trecho do texto integral:\n{fulltext[:6000]}\n\n"
                "Escreva, em português acadêmico, uma seção adicional de "
                "análise crítica aprofundada (3 parágrafos) avaliando rigor "
                "metodológico, diálogo com a literatura e aplicabilidade ao "
                "tema de pesquisa. Use citações no formato ABNT (Autor, ano)."
            )
            extra = client.generate(
                prompt,
                system="Você é um pesquisador acadêmico PhD especializado "
                       "em resenhas críticas Qualis A1.",
                max_tokens=1200,
            )
            if extra:
                meta = client.describe()
                origem = (f"modelo local `{meta['model']}` via Ollama"
                          if meta["local"] else
                          f"modelo `{meta['model']}` via API")
                p = Path(resenha_path)
                p.write_text(
                    p.read_text(encoding="utf-8") +
                    "\n\n## Análise aprofundada (assistida por IA — "
                    f"{origem})\n\n" + extra + "\n",
                    encoding="utf-8")
                return True
        except Exception as exc:
            logger.debug(f"enriquecimento LLM indisponível: {exc}")
        return False
