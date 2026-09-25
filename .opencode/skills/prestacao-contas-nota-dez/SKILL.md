---
name: prestacao-contas-nota-dez
description: Auditoria e execução de resposta a diligências do Prêmio Escola Nota Dez (SEDUC/CE). Use para PDFs escaneados de diligências de prestação de contas (FECOP/Prêmio Escola Nota 10): extração OCR, parse de apontamentos, checklist item-a-item, score interno de cobertura, minuta de ofício-resposta e planilha de controle. NÃO é aprovação do órgão concedente; toda entrega exige revisão humana.
disable-model-invocation: true
---

# Skill: Auditor e Executor de Prestação de Contas (Escola Nota 10)

Plugin no diretório `prestacao_contas_nota_dez/` (SPEC R597).

## Quando usar
- Recebeu uma **diligência** da SEDUC/13ª CREDE sobre prestação de contas do
  **Prêmio Escola Nota Dez** (FECOP) e precisa organizar a resposta.
- Precisa extrair os apontamentos ("DEMANDAS") de um PDF **escaneado** e
  montar checklist + minuta.

## Passo a passo
1. **OCR**: `python3 -m prestacao_contas_nota_dez.src.cli audit "<pdf>" --out exemplos/`
   - Requer `pdftoppm` e `tesseract` com idioma `por` (checado pelo próprio script).
   - Cache em `/tmp/opencode/pcn_ocr_cache` (não polui o repo).
2. **Auditoria**: o comando gera `audit_<nome>.json` com cabeçalho, blocos,
   demandas (com página referida) e score interno de cobertura.
3. **Executor**: `python3 -m prestacao_contas_nota_dez.src.cli execute exemplos/audit_<nome>.json`
   → gera `minuta_<nome>.md` (tabela Item | Exigência | Resposta | Anexo | Pendência),
   `controle_<nome>.csv` (estados documental/tramitação) e `relatorio_<nome>.md`
   (conferência com anti-overclaim).
4. **Preenchimento assistido (revisão humana obrigatória)**:
   `python3 -m prestacao_contas_nota_dez.src.cli sugerir exemplos/audit_<nome>.json`
   → gera `sugestoes_<nome>.md` (tema, página do manual, providência e fundamento
   propostos). Para aplicar nas células da minuta com marcador `[SUGESTÃO – REVISAR]`:
   `... execute ... --aplicar`. Nenhuma sugestão é definitiva; confira o trecho do
   manual na imagem do PDF e a norma do exercício antes de adotar.
4. **Verificação base**: `verificacao.carregar_checklist_base()` lê as 40 verificações
   C01–C40 (grupos: Identificação, Governança, Plano, Contratação, Fiscal, Financeiro,
   Tributos, Bonificação, Cooperação, Patrimônio, Obras, Prazo, Integridade,
   Elegibilidade, Fechamento). `src/conciliar.py` faz conciliação aritmética de escopo.
4. **Referências obrigatórias** (dir `prestacao_contas_nota_dez/references/`):
   - `manual-2019-ocr.md` — OCR do manual 2019 (imagem prevalece; há lacunas).
   - `modelo-resposta.md` — estrutura editorial da resposta (tabela item | exigência | resposta | anexo | pendência).
   - `checklist-base.csv`, `regras-comuns.md`, `base-documental.md`, `fontes-oficiais.md` — conferência documental.
   - `src/conciliar.py` — conciliação aritmética de escopo financeiro.
5. **Revisão humana obrigatória**: conferir cada providência contra a
   documentação original e a legislação (ex.: Lei 8.666/93, manual Mais PAIC,
   capítulo pertinente do manual do Prêmio Escola Nota 10) antes de protocolar.

## Regras invioláveis
- **Score é interno** (cobertura dos apontamentos parseados) — nunca apresentar
  como aprovação do órgão concedente (anti-overclaim R110 / CORRIGENDUM.md).
- **Minutas não são ofícios oficiais**: campos de providência/documento e
  assinaturas são preenchidos pelo responsável pela unidade executora.
- Prestação de contas de recursos públicos é domínio sensível: o plugin é
  apoio computacional; a decisão final é humana e do órgão de controle.
- Sempre registrar o ciclo no `EvolutionRegistry` após executar o pipeline.

## Referência de saída esperada
- `audit_*.json` → estrutura JSON {fonte, doc{cabecalho, blocos[{titulo, demandas[{texto, pagina}], metadados}]}, checklist[{id, bloco, demanda, pagina, providencia, documento, status}], score{total, atendidos, pendentes, cobertura}}.
- `minuta_*.md` → ofício-resposta com um bloco por demanda, campos a preencher.
- `controle_*.csv` → id, bloco, demanda, pagina, providencia, documento, status.