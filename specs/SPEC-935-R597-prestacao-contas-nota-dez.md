# SPEC-935-R597 — Plugin Auditor e Executor de Prestação de Contas (Prêmio Escola Nota Dez)

- **Estado:** implementado (TDD GREEN 8/8)
- **Ciclo:** R597 (EvolutionRegistry)

## Contexto

O usuário recebeu da SEDUC/CE (13ª CREDE) **diligências** sobre a prestação de
contas do **Prêmio Escola Nota Dez** (FECOP) da unidade executora **Conselho
Escolar da Escola de Cidadania Airam Veras** (Crateús-CE), em PDFs escaneados
(Epson Scan 2, sem camada de texto):

| Arquivo | Páginas | Conteúdo |
|---|---|---|
| `img20260924_14524484.pdf` | 15 | Diligência — NE 18109/2016, R$ 24.500,00 |
| `img20260924_15174538.pdf` | 12 | Diligência — Processo 05158910/2019, NE 18984/2018, R$ 24.500,00 |
| `img20260924_15382805.pdf` | 34 | Manual de Orientações (PARF, 2019) — referência normativa |

## Objetivo

Plugin **auditor e executor** que: (1) extrai os apontamentos da diligência via
OCR; (2) organiza checklist item-a-item com página referida; (3) gera **minuta**
de ofício-resposta e planilha de controle — sempre **sob revisão humana**.

## Critérios de aceitação (gate)

1. `pytest prestacao_contas_nota_dez/tests/` → 26/26 verdes (R597 8 + R597b 8 + R597c assistente 10).
2. `audit <pdf>` produz `audit_<nome>.json` com `{fonte, doc{cabecalho, blocos, total_demandas}, checklist[], score{cobertura}}` a partir de PDF real escaneado.
3. Cabeçalho parseado contém: processo, unidade executora, município, CNPJ, NE, valor, ano.
4. `execute <json>` gera `minuta_<nome>.md` (formato administrativo com tabela Item | Exigência | Resposta | Anexo | Pendência), `controle_<nome>.csv` (com estados documental/tramitação) e `relatorio_<nome>.md` (conferência com anti-overclaim).
5. Anti-overclaim R110: score é cobertura interna; nenhum texto declara aprovação do órgão concedente.
6. Skill wrapper com `disable-model-invocation: true` (padrão R595) e `plugin.json` no schema agent-plugins.
7. Referências do plugin `contas-escolares-airam-veras` integradas em `references/` (checklist-base C01–C40, manual-2019-ocr, modelo-resposta) e conciliação aritmética em `src/conciliar.py`.

## Restrições / lições aplicadas

- Detecção de títulos: **não** usar `isupper()` (falha com `Nº` U+00BA); usar `upper() == linha` e excluir linhas de conteúdo (`OBJETO DA`, `DATA DA`, `MAPA COMPARATIVO`, `REFERÊNCIA DA`...).
- `VALOR:` pode vir sem `R$` → moeda opcional no regex.
- Dedup por texto normalizado (OCR repete cabeçalhos por página).
- Domínio sensível (recursos públicos) → fail-closed: itens nascem `pendente`, só `atendido` com providência + documento preenchidos por humano.

## Entregáveis

```
prestacao_contas_nota_dez/
├── plugin.json / README.md
├── src/{ocr,diligencia,auditor,executor,verificacao,relatorio,assistente,conciliar,cli}.py
├── references/  # regras-comuns, base-documental, fontes-oficiais, manual-2019-ocr, checklist-base.csv, modelo-resposta, proveniencia
├── tests/test_r597_prestacao_contas.py + test_r597b_melhorias_plugin.py + test_r597c_assistente.py
└── exemplos/  # audit_*.json, minuta_*.md, controle_*.csv, relatorio_*.md, sugestoes_*.md das 2 diligências
.opencode/skills/prestacao-contas-nota-dez/SKILL.md
```

## Resultado real (validação)

- Diligência 2016: 67 itens de checklist (pós-dedup de 83 brutos), minuta + relatório + sugestões gerados.
- Diligência 2018: 75 itens, minuta + relatório + sugestões gerados.
- Score inicial 0.0 (tudo pendente) — esperado até preenchimento humano.
- Preenchimento assistido: 142 sugestões (2016: 67; 2018: 75) classificadas por tema com página do manual e marcador `[SUGESTÃO – REVISAR]`.
- Conciliação aritmética validada: 24.500,00 + 12,34 − 2.450,00 − 3,50 = 22.058,84 = saldo banco (`valores_conciliados`).