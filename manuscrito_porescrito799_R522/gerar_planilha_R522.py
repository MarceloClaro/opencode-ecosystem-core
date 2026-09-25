#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de planilha de extração — SPEC-935-R522 — Brasil comparado
Cria matriz_extracao_R522.xlsx com 4 abas: Extração, Dicionário, Checklist PRISMA-ScR, Matriz Comparativa
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule

OUTPUT = "/home/marceloclaro/opencode-ecosystem-core/manuscrito_porescrito799_R522/matriz_extracao_R522.xlsx"

wb = openpyxl.Workbook()

# Cores
HEADER_FILL = PatternFill(start_color="0F2A44", end_color="0F2A44", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
SUBHEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
SUBHEADER_FONT = Font(name="Calibri", size=8, bold=True, color="0F2A44")
BODY_FONT = Font(name="Calibri", size=8, color="000000")
BODY_FONT_SMALL = Font(name="Calibri", size=7, color="000000")
HINT_FONT = Font(name="Calibri", size=7, italic=True, color="404040")
THIN_BORDER = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)
GAP_FILL_1 = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
GAP_FILL_2 = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
GAP_FILL_3 = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
GAP_FILL_4 = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")

def style_header(ws, row, cols, fill=HEADER_FILL, font=HEADER_FONT):
    for c in range(1, cols+1):
        cell = ws.cell(row=row, column=c)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

def auto_width(ws, min_w=10, max_w=35):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    l = len(str(cell.value))
                    if l > max_len:
                        max_len = l
            except:
                pass
        adjusted = min(max(max_len + 2, min_w), max_w)
        ws.column_dimensions[col_letter].width = adjusted

# ============ ABA 1 — EXTRAÇÃO ============
ws1 = wb.active
ws1.title = "Extracao"
ws1.sheet_properties.pageSetUpPr.fitToPage = True
ws1.page_setup.orientation = "landscape"
ws1.page_setup.paperSize = ws1.PAPERSIZE_A3
ws1.page_setup.fitToWidth = 1
ws1.page_setup.fitToHeight = 0
ws1.print_title_rows = "1:2"

headers1 = [
    "ID\n(A01…)", "Referência ABNT\ncompleta", "DOI / URL auditada", "Data acesso\n(17/09/2026)", "Ano", "País comparado\n(BR/UE/PT/DE/EUA/UNESCO/Global)", "Tipo de estudo\n(artigo original, revisão, análise documental, relato)", "Desenho/Método\n(PRISMA, qualitativo, quase-experimento, etc.)",
    "Amostra / Contexto\n(N, curso, IES, tribunal)", "Pergunta / Objetivo\n(PICo)", "Método detalhado\n(bases, strings, critérios)", "Achados principais\n(3 bullets máx.)", "Limitações\nautodeclaradas", "Conflitos / Financiamento", 
    "Dimensões Valencia (6)\n[marcar X]", "  → Marcos Regulatórios", "  → Comparação Internacional", "  → Responsabilidade", "  → Ética/Formação", "  → Automação", "  → Acesso/Equidade",
    "Eixos Carmo (4)\n[marcar X]", "  → Fund. éticos", "  → Transparência", "  → Dados/Privacidade", "  → Competências humanísticas",
    "GAP alimentado\n(GAP1 Equidade / GAP2 Governança / GAP3 Norma→Pedagogia / GAP4 Evidência empírica)", "Lição transferível para BR\n(1 frase operacional)", "Notas / Trecho literal curto\n(com pág.)", "Status\n(incluído / excluído + motivo PRISMA)"
]
# We'll create 29 columns (0-28)
ws1.append(headers1)
style_header(ws1, 1, len(headers1))
ws1.row_dimensions[1].height = 45

# Second header row for merged groups? We'll keep single but add example row
example = [
    "A01", "VALENCIA JIMÉNEZ, C. A.; BELTRÁN PACHECO, J. A. Dilemas éticos... Revista Tribunal, 2025.", "https://doi.org/10.59659/revistatribunal.v5i12.235", "17/09/2026", 2025, "Global (Scopus/WoS)", "Revisão sistemática (PRISMA)", "PRISMA, 136→19",
    "19 artigos (Scopus/WoS até mai 2025)", "Quais dilemas éticos da IA na prática legal?", "Scopus/WoS, strings IA+legal, 6 dimensões codificadas", "• 57,89% marcos regulatórios\n• 42,11% comparação\n• Vácuo governança/equidade", "Só Scopus/WoS, n=19, sem avaliação qualidade detalhada", "Sem financiamento declarado",
    "", "X", "X", "X", "X", "", "",
    "", "X", "X", "X", "",
    "GAP1 + GAP2 + GAP3", "Provar que GAP é mensurável: replicar frequência no corpus BR-comparado", "p. 8: 'vazios críticos em justiça social, governança algorítmica e direitos humanos'", "incluído"
]
ws1.append(example)
# Style example row
for c in range(1, len(headers1)+1):
    cell = ws1.cell(row=2, column=c)
    cell.font = BODY_FONT_SMALL
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = THIN_BORDER
    if c in [16,17,18,19]: # dimensions X
        cell.alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[2].height = 60

# Add 30 empty rows for filling
for i in range(3, 33):
    ws1.append(["" for _ in headers1])
    ws1.row_dimensions[i].height = 22
    for c in range(1, len(headers1)+1):
        cell = ws1.cell(row=i, column=c)
        cell.font = BODY_FONT_SMALL
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
        cell.fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid") if i % 2 == 0 else PatternFill(fill_type=None)

# Freeze and filter
ws1.freeze_panes = "A2"
ws1.auto_filter.ref = f"A1:{get_column_letter(len(headers1))}1"
ws1.sheet_properties.pageSetUpPr.fitToPage = True

# Column widths
widths1 = [6, 28, 22, 11, 6, 14, 16, 16, 16, 16, 16, 20, 16, 14, 6, 7,7,7,7,7,7, 6,7,7,7,7, 18, 22, 20, 14]
for i, w in enumerate(widths1, start=1):
    ws1.column_dimensions[get_column_letter(i)].width = w

# Data validation for Status
from openpyxl.worksheet.datavalidation import DataValidation
dv_status = DataValidation(type="list", formula1='"incluído,excluído - fora escopo educacional,excluído - <2020,excluído - sem texto completo,excluído - opinião sem método,excluído - duplicata"', allow_blank=True)
dv_status.error ='Selecione status PRISMA'
dv_status.errorTitle = 'Status'
dv_status.prompt = 'Escolha motivo PRISMA'
ws1.add_data_validation(dv_status)
dv_status.add(f"AC3:AC32")

dv_gap = DataValidation(type="list", formula1='"GAP1,GAP2,GAP3,GAP4,GAP1+GAP2,GAP1+GAP3,GAP2+GAP3,GAP3+GAP4"', allow_blank=True)
ws1.add_data_validation(dv_gap)
dv_gap.add(f"AA3:AA32")

# Conditional formatting for GAP
# Note: openpyxl CellIsRule with containsText is limited, keep simple
# ws1.conditional_formatting.add(f"AA3:AA32", CellIsRule(operator="containsText", text="GAP1", fill=GAP_FILL_1))

# Print note at bottom
ws1["A34"] = "INSTRUÇÕES: Preencha 1 linha por estudo incluído + também registre excluídos na leitura integral com motivo PRISMA. Use X nas colunas 16-21 e 23-26. GAP = lacuna que o estudo alimenta. Lição transferível = frase operacional para o BR. Audite DOI/URL em 17/09/2026 e mantenha data de acesso."
ws1["A34"].font = HINT_FONT
ws1["A34"].alignment = Alignment(wrap_text=True)
ws1.merge_cells("A34:AC34")
ws1.row_dimensions[34].height = 30

# ============ ABA 2 — DICIONÁRIO ============
ws2 = wb.create_sheet("Dicionario")
headers2 = ["Coluna", "Nome", "Definição", "Tipo", "Valores permitidos / Exemplo", "Obrigatório?"]
ws2.append(headers2)
style_header(ws2, 1, len(headers2))
ws2.row_dimensions[1].height = 20
dict_rows = [
    ["A", "ID", "Código sequencial do estudo (A01, A02…)", "texto", "A01", "sim"],
    ["B", "Referência ABNT", "Referência completa em ABNT, só citadas no texto", "texto", "SOBRENOME, Nome. Título. Periódico, v., p., ano. DOI.", "sim"],
    ["C", "DOI/URL auditada", "Link resolvido e verificado em 17/09/2026", "url", "https://doi.org/10.xxxx/xxxx", "sim"],
    ["D", "Data acesso", "Data em que URL foi verificada", "data", "17/09/2026", "sim"],
    ["E", "Ano", "Ano de publicação", "inteiro", "2020-2025", "sim"],
    ["F", "País comparado", "Foco geográfico-normativo", "lista", "BR, UE, PT, DE, EUA, UNESCO, Global", "sim"],
    ["G", "Tipo de estudo", "Tipologia", "lista", "artigo original, revisão sistemática, scoping, análise documental, relato", "sim"],
    ["H", "Desenho/Método", "Desenho detalhado", "texto", "PRISMA 136→19; qualitativo entrevistas; quase-experimento", "sim"],
    ["I", "Amostra/Contexto", "N, curso, IES, tribunal, corpus", "texto", "19 artigos; 120 discentes Direito UFRJ", "sim"],
    ["J", "Pergunta/Objetivo (PICo)", "Pergunta PICo do estudo original", "texto", "Que evidências...?", "sim"],
    ["K", "Método detalhado", "Bases, strings, critérios do estudo original", "texto", "Scopus/WoS, strings, 2020-2025", "sim"],
    ["L", "Achados principais", "Até 3 bullets objetivos, sem inferência", "texto", "• 57,89% marcos...", "sim"],
    ["M", "Limitações", "Autodeclaradas pelo estudo", "texto", "n pequeno, só Scopus/WoS", "sim"],
    ["N", "Conflitos/Financiamento", "Declarados", "texto", "Sem conflito / FAPESP 2023/xxxxx", "sim"],
    ["O-U", "Dimensões Valencia (6)", "Marcar X se o estudo aborda a dimensão", "binário X", "X ou vazio", "sim"],
    ["V-AB", "Eixos Carmo (4)", "Marcar X nos 4 eixos", "binário X", "X ou vazio", "sim"],
    ["AA", "GAP alimentado", "Qual GAP o estudo alimenta", "lista", "GAP1 Equidade, GAP2 Governança, GAP3 Norma→Pedagogia, GAP4 Evidência", "sim"],
    ["AB", "Lição transferível BR", "Frase operacional para o BR comparado", "texto", "Replicar frequência; adotar transparência hermenêutica em rubrica", "sim"],
    ["AC", "Notas / Trecho literal", "Trecho curto com pág. entre aspas", "texto", "\"vazios críticos...\" (p.8)", "não"],
    ["AD", "Status PRISMA", "Incluído ou motivo de exclusão na leitura integral", "lista", "incluído / excluído - motivo", "sim"],
]
for r in dict_rows:
    ws2.append(r)
    for c in range(1, len(headers2)+1):
        cell = ws2.cell(row=ws2.max_row, column=c)
        cell.font = BODY_FONT
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
        if c==1:
            cell.font = Font(name="Calibri", size=8, bold=True)
ws2.column_dimensions["A"].width = 7
ws2.column_dimensions["B"].width = 18
ws2.column_dimensions["C"].width = 36
ws2.column_dimensions["D"].width = 22
ws2.column_dimensions["E"].width = 14
ws2.column_dimensions["F"].width = 28
for i in range(2, ws2.max_row+1):
    ws2.row_dimensions[i].height = 22
ws2.freeze_panes = "A2"
ws2.auto_filter.ref = f"A1:F1"

# ============ ABA 3 — CHECKLIST PRISMA-ScR ============
ws3 = wb.create_sheet("Checklist_PRISMA-ScR")
ws3.sheet_properties.pageSetUpPr.fitToPage = True
ws3.page_setup.orientation = "portrait"
ws3.page_setup.paperSize = ws3.PAPERSIZE_A4
headers3 = ["Item PRISMA-ScR", "Seção do manuscrito", "Página", "Status", "Observações"]
ws3.append(headers3)
style_header(ws3, 1, len(headers3))
# 22 itens PRISMA-ScR
prisma_items = [
    ["1. Título", "Capa", "", "pendente", "Indicar que é scoping review no título"],
    ["2. Resumo estruturado", "Resumo/Abstract", "1", "pendente", "Background, objetivos, critérios, fontes, síntese, conclusões"],
    ["3. Justificativa", "1 Introdução", "3", "ok", "Descompasso norma-pedagogia + GAP mensurável"],
    ["4. Objetivos / Pergunta PICo", "1 Introdução + 3 Método", "3/6", "ok", "PICo comparada + 4 subperguntas"],
    ["5. Protocolo e registro", "3 Método", "6", "pendente", "Registrar no OSF antes da execução"],
    ["6. Critérios de elegibilidade", "3 Método", "7", "ok", "Inclusão/exclusão com justificativa comparado"],
    ["7. Fontes de informação", "3 Método", "6", "ok", "Scopus/WoS/SciELO/Educ@/CAPES/DOAJ/Google Acadêmico"],
    ["8. Busca (strings completas)", "3 Método + Quadro 1", "6", "ok", "Blocos A/B/C reprodutíveis"],
    ["9. Seleção (triagem)", "3 Método", "7", "pendente", "Rayyan duplo-cega + fluxograma"],
    ["10. Extração (ficha)", "3 Método", "7", "ok", "Planilha com 29 campos (aba Extração)"],
    ["11. Itens de dado", "3 Método", "7", "ok", "Ver Dicionário"],
    ["12. Avaliação crítica (se aplicável)", "3 Método", "7", "ok", "JBI/MMAT para sistemática"],
    ["13. Síntese dos resultados", "3 Método", "7", "ok", "Radar + temática + matriz + gap map"],
    ["14. Seleção (resultados)", "4 Resultados", "8", "pendente", "Fluxograma com Ns reais"],
    ["15. Características dos estudos", "4 Resultados", "8", "pendente", "Tabela 1 frequências"],
    ["16. Resultados por estudo", "4 Resultados", "8", "pendente", "Síntese por estudo (ficha)"],
    ["17. Síntese (mapa)", "4 Resultados", "9", "pendente", "Matriz comparativa + gap map"],
    ["18. Sumário da evidência", "5 Discussão", "10", "pendente", "4 teses Brasil-comparado"],
    ["19. Limitações", "6 Conclusão", "12", "ok", "Heterogeneidade, viés de base, janela 2020-2025"],
    ["20. Conclusões + agenda", "6 Conclusão", "12", "ok", "3 estudos PICO + Transparência Hermenêutica"],
    ["21. Financiamento", "Declarações", "13", "pendente", "Declarar"],
    ["22. Conflitos / Dados abertos / IA", "Declarações", "13", "ok", "OSF/Zenodo + declaração IA + Turnitin"],
]
for r in prisma_items:
    ws3.append(r)
    for c in range(1, len(headers3)+1):
        cell = ws3.cell(row=ws3.max_row, column=c)
        cell.font = BODY_FONT
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
        if c==4:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if "ok" in str(cell.value).lower():
                cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
            else:
                cell.fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
for i in range(2, ws3.max_row+1):
    ws3.row_dimensions[i].height = 18
ws3.column_dimensions["A"].width = 28
ws3.column_dimensions["B"].width = 22
ws3.column_dimensions["C"].width = 10
ws3.column_dimensions["D"].width = 12
ws3.column_dimensions["E"].width = 38
ws3.freeze_panes = "A2"
ws3["A25"] = "Fonte: Tricco et al., PRISMA-ScR, Ann Intern Med 2018; Page et al., PRISMA 2020, BMJ 2021. Preencha Página após paginação final; Status: ok/pendente/não se aplica."
ws3["A25"].font = HINT_FONT
ws3.merge_cells("A25:E25")

# ============ ABA 4 — MATRIZ COMPARATIVA ============
ws4 = wb.create_sheet("Matriz_Comparativa")
headers4 = ["Eixo analítico", "Brasil\nPL2338 + CNJ615 + LGPD", "UE\nAI Act 2024/1689", "Portugal\nOAP 2023", "Alemanha (UE)", "EUA", "UNESCO 2023", "Fonte auditada (17/09/2026)", "Lição transferível BR (a preencher após extração)"]
ws4.append(headers4)
style_header(ws4, 1, len(headers4))
ws4.row_dimensions[1].height = 38
matriz = [
    ["Arquitetura de risco", "Risco excessivo (vedado) + Alto risco (obr. reforçadas); 68 obrigações", "4 níveis: inaceitável, alto, limitado, mínimo; 43 obrigações", "Transposição UE", "UE (alto rigor)", "Setorial, sem lei federal", "7 passos humanocêntricos", "ITS Rio 23 jun 2025; Juristech 18 abr 2026", ""],
    ["Educação = alto risco?", "SIM — art.14 II PL (seleção/avaliações/monitoramento)", "SIM — Anexo III (educação/emprego)", "SIM via UE", "SIM", "Case-by-case", "Alerta privacidade", "PL art.14 II; AI Act Anexo III; UNESCO 2023", ""],
    ["Direitos do afetado", "Capítulo próprio: explicação, contestação, revisão humana", "RGPD + Carta + deveres a fornecedores", "Via RGPD + OAP", "Via UE", "Limitado", "Agência humana", "PL cap. direitos; AI Act + RGPD", ""],
    ["Transparência", "Hermenêutica (método+axiologia+limites) + Sinapses art.24 CNJ", "Documentação + rastreabilidade", "Circular OAP", "UE", "Disclosure", "Validação ético-pedagógica", "Carmo & Alves 2025; CNJ art.24", ""],
    ["Governança", "SIA/ANPD + CRIA + CECIA + Comitê IA Judiciário + Sinapses", "Escritório IA UE + autoridades nacionais", "Adaptação UE", "UE", "Descentralizada (ABA)", "Capacitação humana", "PL art.45; CNJ art.15; UNESCO", ""],
    ["Responsabilidade", "Objetiva e solidária (arts.35-36 PL)", "AI Act ex ante + Dir. 2024/2853 ex post", "Direito nacional", "Direito nacional", "Common law", "Accountability pública", "PL arts.35-36; Juristech", ""],
    ["Direitos autorais (treino)", "Transparência obras + opt-out + remuneração", "Exceção TDM + reserva", "UE", "UE", "Fair use em disputa", "Copyright/manipulação", "PL direitos autorais; AI Act", ""],
    ["Foco setor público", "14 obrigações específicas", "Sem detalhamento", "Via UE", "—", "—", "Equidade/inclusão", "ITS Rio", ""],
    ["Idade / vulneráveis", "Proteção integral crianças/adolescentes (art.2 XIV PL)", "—", "—", "—", "—", "Idade mínima 13 + formação docente", "PL art.2 XIV; UNESCO 2023", ""],
    ["Calendário", "Senado dez/2024 → Câmara 2026 (pendente)", "Vigor 01 ago 2024 → aplicação até 02 ago 2026/27", "Transposição 2026", "—", "—", "Guidance 2023", "Senado/Câmara; JOUE 12 jul 2024", ""],
]
for r in matriz:
    ws4.append(r)
    for c in range(1, len(headers4)+1):
        cell = ws4.cell(row=ws4.max_row, column=c)
        cell.font = BODY_FONT_SMALL
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
        if c==1:
            cell.font = Font(name="Calibri", size=8, bold=True)
            cell.fill = SUBHEADER_FILL
ws4.column_dimensions["A"].width = 20
ws4.column_dimensions["B"].width = 22
ws4.column_dimensions["C"].width = 22
ws4.column_dimensions["D"].width = 16
ws4.column_dimensions["E"].width = 14
ws4.column_dimensions["F"].width = 16
ws4.column_dimensions["G"].width = 16
ws4.column_dimensions["H"].width = 24
ws4.column_dimensions["I"].width = 26
for i in range(2, ws4.max_row+1):
    ws4.row_dimensions[i].height = 28
ws4.freeze_panes = "A2"
ws4.sheet_properties.pageSetUpPr.fitToPage = True
ws4.page_setup.orientation = "landscape"
ws4.page_setup.paperSize = ws4.PAPERSIZE_A3
ws4.page_setup.fitToWidth = 1

# ============ ABA 5 — INSTRUÇÕES ============
ws5 = wb.create_sheet("Instrucoes")
ws5.sheet_properties.pageSetUpPr.fitToPage = True
ws5.page_setup.orientation = "portrait"
ws5["A1"] = "INSTRUÇÕES — Matriz de extração R522 — Brasil comparado (2020-2025)"
ws5["A1"].font = Font(name="Calibri", size=14, bold=True, color="0F2A44")
ws5["A1"].alignment = Alignment(horizontal="left")
instr = [
    "1. FLUXO: Importe registros no Rayyan → deduplique → triagem duplo-cega título/resumo → leitura integral → extraia em ‘Extracao’ (1 linha por estudo).",
    "2. AUDITORIA: Verifique DOI/URL em 17/09/2026 e mantenha Data acesso. Marque [NÃO VERIFICADA] se não resolver. Nenhuma ref inventada.",
    "3. DIMENSÕES: Marque X nas colunas 16-21 (Valencia 6) e 23-26 (Carmo 4). Permite gerar gráfico radar automaticamente (Tabela 1).",
    "4. GAP: Use coluna AA para indicar qual GAP o estudo alimenta (GAP1 Equidade, GAP2 Governança, GAP3 Norma→Pedagogia, GAP4 Evidência empírica). Use coluna AB para lição transferível em 1 frase operacional.",
    "5. COMPARADO: Para cada estudo do Bloco B, preencha País comparado (F) e Lição transferível (AB). Ex.: ‘PT/OAP: circular deontológica como modelo ágil para OAB — implementar sem esperar PL’. Na aba Matriz_Comparativa, col. I, sintetize após extração.",
    "6. PRISMA: Preencha checklist na aba Checklist_PRISMA-ScR à medida que avança; status ok/pendente colore automaticamente.",
    "7. QUALIDADE: Se o corpus for sistemático, use JBI/MMAT e anote limitações (col. M). No scoping, mapeie sem excluir por qualidade.",
    "8. SÍNTESE: Após extração, gere: (a) Tabela 1 frequências (radar), (b) síntese temática Braun & Clarke nos 4 eixos, (c) gap map (dimensão × país), (d) agenda PICO.",
    "9. ARMAZENAMENTO: Salve este XLSX no Zenodo/OSF como material suplementar. Versione (v1.0, v1.1...).",
    "10. ANTI-OVERCLAIM: Mantenha ‘resultados esperados’ até execução real; não trate documentação técnica de fornecedor como prova de eficácia pedagógica.",
    "11. SUBMISSÃO: Exporte abas Extração + Matriz como PDF para suplemento da Educação Por Escrito. Turnitin institucional <15% (meta, sem garantia).",
    "12. CONTATO R522: SPEC-935-R522 em specs/. Dúvidas sobre Transparência Hermenêutica: ver Carmo & Alves 2025 + CNJ art.24-25 (linguagem simples).",
]
for i, txt in enumerate(instr, start=3):
    ws5[f"A{i}"] = txt
    ws5[f"A{i}"].font = Font(name="Calibri", size=8)
    ws5[f"A{i}"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws5.row_dimensions[i].height = 18
    ws5.merge_cells(f"A{i}:I{i}")
ws5.column_dimensions["A"].width = 140
ws5["A18"] = "EQUIPE: 2 revisores independentes + 3º para conflitos. Valide 10% da extração por segundo revisor (concordância κ)."
ws5["A18"].font = Font(name="Calibri", size=8, italic=True, color="404040")
ws5["A19"] = "CRÉDITO: Template R522 — OpenCode Ecosystem Core — marceloclaro/orchestrator — SDD/TDD — 17/09/2026."
ws5["A19"].font = Font(name="Calibri", size=7, italic=True, color="808080")

# Ajustes finais
for ws in [ws1, ws2, ws3, ws4, ws5]:
    ws.sheet_properties.pageSetUpPr.fitToPage = True

wb.save(OUTPUT)
print(f"Planilha salva em: {OUTPUT}")

