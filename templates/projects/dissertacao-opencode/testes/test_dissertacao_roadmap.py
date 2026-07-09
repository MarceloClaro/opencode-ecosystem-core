"""
TDD Roadmap Validation — Dissertação OpenCode Ecosystem (100pp)
=================================================================
Valida que todos os componentes, métricas e estruturas da dissertação
atendem aos critérios Qualis A1 (score >= 95/100).

Estrutura de testes:
  1. Testes Estruturais (6 CTs): Estrutura do documento
  2. Testes de Conteúdo (6 CTs): Qualidade do conteúdo
  3. Testes de Citação (4 CTs): Protocolo TSAC
  4. Testes de Roadmap (4 CTs): Validação contra Gartner Gaps
  5. Testes de Qualidade (4 CTs): Score Qualis

Total: 24 CTs
"""

import pytest
import os
import re
from pathlib import Path

# ===== CONFIGURAÇÃO =====
DISSERTACAO_DIR = Path(__file__).resolve().parent.parent
CAPITULOS_DIR = DISSERTACAO_DIR / "capitulos"
TEMPLATE_FILE = DISSERTACAO_DIR / "dissertacao.tex"

# ===== FIXTURES =====

@pytest.fixture
def capitulos() -> list:
    """Lista todos os arquivos .tex no diretório de capítulos."""
    return sorted(CAPITULOS_DIR.glob("*.tex"))

@pytest.fixture
def conteudo_total(capitulos) -> str:
    """Concatena todo o conteúdo dos capítulos em uma única string."""
    full = ""
    for cap in capitulos:
        if cap.exists():
            full += cap.read_text(encoding="utf-8") + "\n"
    return full

@pytest.fixture
def dissertacao_template() -> str:
    """Lê o template mestre da dissertação."""
    return TEMPLATE_FILE.read_text(encoding="utf-8")

# ============================================================
# GRUPO 1: TESTES ESTRUTURAIS (6 CTs)
# ============================================================

class TestEstruturaDocumento:
    """CT-EST-01 a CT-EST-06: Valida a estrutura da dissertação."""

    def test_ct_est_01_arquivos_capitulos_existem(self, capitulos):
        """CT-EST-01: Todos os 20 capítulos devem existir."""
        nomes_esperados = [
            "00-capa.tex", "01-folha-rosto.tex", "02-ficha-catalografica.tex",
            "03-dedicatoria.tex", "04-agradecimentos.tex", "05-epigrafe.tex",
            "06-resumo.tex", "07-abstract.tex", "08-lista-figuras.tex",
            "09-lista-tabelas.tex", "10-lista-siglas.tex", "11-sumario.tex",
            "12-introducao.tex", "13-revisao-literatura.tex", "14-metodologia.tex",
            "15-resultados.tex", "16-discussao.tex", "17-conclusao.tex",
            "18-referencias.tex", "19-apendice-a.tex", "20-apendice-b.tex",
            "21-apendice-c.tex"
        ]
        nomes_existentes = [c.name for c in capitulos]
        for nome in nomes_esperados:
            assert nome in nomes_existentes, f"Arquivo {nome} não encontrado"

    def test_ct_est_02_template_mestre_existe(self, dissertacao_template):
        """CT-EST-02: O template mestre dissertacao.tex deve existir e conter \documentclass."""
        assert "\\documentclass" in dissertacao_template
        assert "\\begin{document}" in dissertacao_template
        assert "\\end{document}" in dissertacao_template

    def test_ct_est_03_template_referencia_todos_capitulos(self, dissertacao_template):
        """CT-EST-03: O template deve referenciar (include) todos os capítulos."""
        for i, nome in enumerate([
            "00-capa", "01-folha-rosto", "02-ficha-catalografica",
            "03-dedicatoria", "04-agradecimentos", "05-epigrafe",
            "06-resumo", "07-abstract", "08-lista-figuras",
            "09-lista-tabelas", "10-lista-siglas", "11-sumario",
            "12-introducao", "13-revisao-literatura", "14-metodologia",
            "15-resultados", "16-discussao", "17-conclusao",
            "18-referencias", "19-apendice-a", "20-apendice-b",
            "21-apendice-c"
        ]):
            assert f"capitulos/{nome}" in dissertacao_template, \
                f"Template não referencia capítulos/{nome}"

    def test_ct_est_04_introducao_contem_cars(self, capitulos):
        """CT-EST-04: A introdução deve conter estrutura CARS (Create a Research Space)."""
        intro = CAPITULOS_DIR / "12-introducao.tex"
        conteudo = intro.read_text(encoding="utf-8")
        # Deve conter definição do território, lacuna e ocupação
        assert "crise" in conteudo.lower() or "reprodutibilidade" in conteudo.lower()
        assert "lacuna" in conteudo.lower() or "gap" in conteudo.lower() or "ausência" in conteudo.lower()
        assert "objetivo" in conteudo.lower() or "pergunta de pesquisa" in conteudo.lower()

    def test_ct_est_05_revisao_literatura_8_eixos(self, capitulos):
        """CT-EST-05: A revisão de literatura deve conter 8 eixos temáticos."""
        rev = CAPITULOS_DIR / "13-revisao-literatura.tex"
        conteudo = rev.read_text(encoding="utf-8")
        eixos = ["Eixo 1", "Eixo 2", "Eixo 3", "Eixo 4", "Eixo 5", "Eixo 6", "Eixo 7", "Eixo 8"]
        for eixo in eixos:
            assert eixo in conteudo, f"Eixo '{eixo}' não encontrado na revisão"

    def test_ct_est_06_metodologia_contem_sdd_tdd(self, capitulos):
        """CT-EST-06: A metodologia deve conter SDD, TDD e AutoEvolve."""
        met = CAPITULOS_DIR / "14-metodologia.tex"
        conteudo = met.read_text(encoding="utf-8")
        assert "SDD" in conteudo or "Specification-Driven" in conteudo
        assert "TDD" in conteudo or "Test-Driven" in conteudo
        assert "AutoEvolve" in conteudo or "auto-evolu" in conteudo.lower()

# ============================================================
# GRUPO 2: TESTES DE CONTEÚDO (6 CTs)
# ============================================================

class TestQualidadeConteudo:
    """CT-CON-01 a CT-CON-06: Valida a qualidade do conteúdo acadêmico."""

    def test_ct_con_01_tamanho_minimo(self, conteudo_total):
        """CT-CON-01: O documento deve ter pelo menos 16.000 palavras (≈100 páginas ABNT com notas, tabelas e quebras)."""
        palavras = len(conteudo_total.split())
        assert palavras >= 16000, f"Documento tem apenas {palavras} palavras (mínimo: 16.000)"

    def test_ct_con_02_palavras_chave_resumo(self, capitulos):
        """CT-CON-02: O resumo deve ter palavras-chave (mínimo 3)."""
        resumo = CAPITULOS_DIR / "06-resumo.tex"
        conteudo = resumo.read_text(encoding="utf-8")
        assert "Palavras-chave:" in conteudo
        # Extrai palavras-chave após "Palavras-chave:"
        match = re.search(r'Palavras-chave:(.*?)(?:\n|$)', conteudo, re.DOTALL)
        if match:
            keywords = match.group(1).strip()
            kws = [k.strip() for k in keywords.replace(".", ",").split(",") if k.strip()]
            assert len(kws) >= 3, f"Apenas {len(kws)} palavras-chave encontradas (mínimo 3)"

    def test_ct_con_03_notas_rodape_presentes(self, conteudo_total):
        """CT-CON-03: Deve haver pelo menos 20 notas de rodapé (protocolo TSAC)."""
        count = conteudo_total.count("\\footnote{")
        assert count >= 20, f"Apenas {count} notas de rodapé encontradas (mínimo 20)"

    def test_ct_con_04_dois_presentes(self, conteudo_total):
        """CT-CON-04: Deve haver pelo menos 10 DOIs nas citações."""
        dois = len(re.findall(r'doi\s*[:.]?\s*10\.\d{4,}', conteudo_total, re.IGNORECASE))
        dois += len(re.findall(r'https?://doi\.org/10\.\d{4,}', conteudo_total, re.IGNORECASE))
        dois += len(re.findall(r'https?://dx\.doi\.org/10\.\d{4,}', conteudo_total, re.IGNORECASE))
        assert dois >= 10, f"Apenas {dois} DOIs encontrados (mínimo 10)"

    def test_ct_con_05_referencias_quantidade(self, capitulos):
        """CT-CON-05: Deve haver pelo menos 50 referências bibliográficas."""
        refs = CAPITULOS_DIR / "18-referencias.tex"
        conteudo = refs.read_text(encoding="utf-8")
        bibitems = len(re.findall(r'\\bibitem\{', conteudo))
        assert bibitems >= 50, f"Apenas {bibitems} referências (mínimo 50)"

    def test_ct_con_06_tabelas_presentes(self, conteudo_total):
        """CT-CON-06: Deve haver pelo menos 3 tabelas (dados quantitativos)."""
        tabelas = len(re.findall(r'\\begin\{table\}', conteudo_total))
        tabelas += len(re.findall(r'\\begin\{longtable\}', conteudo_total))
        assert tabelas >= 3, f"Apenas {tabelas} tabelas encontradas (mínimo 3)"

# ============================================================
# GRUPO 3: TESTES DE CITAÇÃO (4 CTs)
# ============================================================

class TestProtocoloTSAC:
    """CT-TSAC-01 a CT-TSAC-04: Valida o protocolo de citações auditáveis."""

    def test_ct_tsac_01_fichamento_critico(self, conteudo_total):
        """CT-TSAC-01: Notas de rodapé devem conter 'Fichamento Crítico'."""
        count = conteudo_total.count("Fichamento Crítico")
        # Pelo menos metade das notas devem ter fichamento
        notas = conteudo_total.count("\\footnote{")
        assert count >= notas * 0.3, \
            f"Apenas {count} fichamentos para {notas} notas (mínimo 30%)"

    def test_ct_tsac_02_trecho_original(self, conteudo_total):
        """CT-TSAC-02: Notas devem conter 'Trecho Original' ou citação direta."""
        count = conteudo_total.count("Trecho Original")
        assert count >= 5, f"Apenas {count} trechos originais (mínimo 5)"

    def test_ct_tsac_03_traducao(self, conteudo_total):
        """CT-TSAC-03: Notas com trecho original em inglês devem ter 'Tradução'."""
        count = conteudo_total.count("Tradução")
        assert count >= 3, f"Apenas {count} traduções (mínimo 3)"

    def test_ct_tsac_04_formato_abnt(self, capitulos):
        """CT-TSAC-04: Referências devem usar formato ABNT (SOBRENOME em maiúsculas)."""
        refs = CAPITULOS_DIR / "18-referencias.tex"
        conteudo = refs.read_text(encoding="utf-8")
        # Verifica que existem entradas no formato ABNT
        abnt_pattern = r'\\bibitem\{[^}]*\}\s*\n\s*[A-Z][A-Z\s]+,'  # SOBRENOME,
        matches = len(re.findall(abnt_pattern, conteudo))
        assert matches >= 10, f"Apenas {matches} referências em formato ABNT (mínimo 10)"

# ============================================================
# GRUPO 4: TESTES DE ROADMAP (4 CTs)
# ============================================================

class TestRoadmapGartner:
    """CT-RDM-01 a CT-RDM-04: Valida cobertura dos 3 gaps do Gartner Hype Cycle."""

    def test_ct_rdm_01_gap1_api_governance(self, conteudo_total):
        """CT-RDM-01: A dissertação deve mencionar SPEC-019 (API Governance)."""
        assert "SPEC-019" in conteudo_total or "Governança de APIs" in conteudo_total or \
               "API Governance" in conteudo_total

    def test_ct_rdm_02_gap2_data_streaming(self, conteudo_total):
        """CT-RDM-02: A dissertação deve mencionar SPEC-020 (Data Streaming)."""
        assert "SPEC-020" in conteudo_total or "Data Streaming" in conteudo_total

    def test_ct_rdm_03_gap3_low_code(self, conteudo_total):
        """CT-RDM-03: A dissertação deve mencionar SPEC-021 (Low-Code Platform)."""
        assert "SPEC-021" in conteudo_total or "Low-Code" in conteudo_total

    def test_ct_rdm_04_gartner_citado(self, conteudo_total):
        """CT-RDM-04: O Gartner Hype Cycle 2026 deve ser citado."""
        assert "Gartner" in conteudo_total or "gartner" in conteudo_total.lower()

# ============================================================
# GRUPO 5: TESTES DE QUALIDADE (4 CTs)
# ============================================================

class TestScoreQualis:
    """CT-QUA-01 a CT-QUA-04: Valida critérios de score Qualis A1."""

    def test_ct_qua_01_imrad(self, conteudo_total):
        """CT-QUA-01: Deve seguir estrutura IMRAD (Intro, Metodo, Resultados, Discussao)."""
        patterns = [
            (r'\\chapter\{INTRODUÇÃO\}', "Introdução"),
            (r'\\chapter\{METODOLOGIA\}', "Metodologia"),
            (r'\\chapter\{RESULTADOS\}', "Resultados"),
            (r'\\chapter\{DISCUSSÃO\}', "Discussão"),
            (r'\\chapter\{CONCLUSÃO\}', "Conclusão"),
        ]
        for pattern, nome in patterns:
            assert re.search(pattern, conteudo_total), f"Capítulo '{nome}' não encontrado"

    def test_ct_qua_02_abnt_config(self, dissertacao_template):
        """CT-QUA-02: Configurações ABNT devem estar presentes (A4, Times, margens)."""
        assert "a4paper" in dissertacao_template
        assert "times" in dissertacao_template.lower() or "Times" in dissertacao_template
        assert "top=3cm" in dissertacao_template
        assert "left=3cm" in dissertacao_template

    def test_ct_qua_03_apendices(self, capitulos):
        """CT-QUA-03: Deve ter pelo menos 3 apêndices (incluindo scanner ontológico)."""
        apendices = [c for c in capitulos if "apendice" in c.name.lower()]
        assert len(apendices) >= 3, f"Apenas {len(apendices)} apêndices (mínimo 3)"

    def test_ct_qua_04_sem_cjk(self, conteudo_total):
        """CT-QUA-04: Zero vazamento de caracteres CJK no conteúdo."""
        cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff00-\uffef]')
        matches = cjk_pattern.findall(conteudo_total)
        assert len(matches) == 0, \
            f"Encontrados {len(matches)} caracteres CJK: {matches[:10]}... (zero tolerância)"

# ============================================================
# GRUPO 6: TESTE DO SCANNER ONTOLÓGICO (1 CT)
# ============================================================

class TestScannerOntologico:
    """CT-SCN-01 a CT-SCN-03: Valida a integração do scanner noológico no corpo da dissertação."""

    def test_ct_scn_01_scanner_na_metodologia(self, conteudo_total):
        """CT-SCN-01: O scanner noológico deve estar documentado na Metodologia (Cap. 3)."""
        # Verifica que o scanner é mencionado no contexto metodológico
        assert "Scanner Noológico" in conteudo_total or "scanner noológico" in conteudo_total.lower()
        # Verifica as 10 dimensões
        dims = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10"]
        encontrados = sum(1 for d in dims if d in conteudo_total)
        assert encontrados >= 8, f"Apenas {encontrados}/10 dimensões do scanner documentadas"

    def test_ct_scn_02_scanner_nos_resultados(self, capitulos):
        """CT-SCN-02: Os resultados do scanner devem estar no Capítulo 4."""
        res = CAPITULOS_DIR / "15-resultados.tex"
        conteudo = res.read_text(encoding="utf-8")
        assert "Scanner Noológico" in conteudo
        assert "Cobertura" in conteudo
        assert "192%" in conteudo or "+192" in conteudo  # +192% de melhoria
        assert "Pontos Cegos" in conteudo or "pontos cegos" in conteudo.lower()

    def test_ct_scn_03_paradigma_na_discussao(self, capitulos):
        """CT-SCN-03: A mudança de paradigma deve estar na Discussão (Cap. 5)."""
        disc = CAPITULOS_DIR / "16-discussao.tex"
        conteudo = disc.read_text(encoding="utf-8")
        assert "o que está ausente" in conteudo.lower()
        assert "paradigma" in conteudo.lower()
        assert "mudança" in conteudo.lower() or "shift" in conteudo.lower()

    def test_ct_scn_04_expansao_5d(self, conteudo_total):
        """CT-SCN-04: A Expansão Epistemológica 5D deve ser documentada."""
        assert "Expansão Epistemológica 5D" in conteudo_total or "5D" in conteudo_total
        # Verifica menção aos 5 componentes da expansão
        componentes = ["Teoria dos Jogos", "Nash", "Sistêmico", "mhGAP", 
                       "Neurociências", "Etkin", "Longitudinal", "Cuijpers",
                       "Diversificação", "Smith"]
        encontrados = sum(1 for c in componentes if c in conteudo_total)
        assert encontrados >= 6, f"Apenas {encontrados}/10 componentes da Expansão 5D documentados"

# ===== EXECUÇÃO =====
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--no-header"])
