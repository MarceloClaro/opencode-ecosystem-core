# Auditoria reprodutível — Artigo ARM–Educação (SPEC-935-R408/R412)

Auditoria e reconstrução editorial do manuscrito *A educação como mecanismo de
escape da armadilha da renda média* (135 economias, 1960–2023), com dados
oficiais do World Bank WDI/WGI, protocolo SDD/TDD e gate *fail-closed*.

## Status

**PUBLICAÇÃO BLOQUEADA** — achados críticos persistem na versão original (ver
[RELATORIO_AUDITORIA.md](RELATORIO_AUDITORIA.md)). Este pacote é uma
reconstrução diagnóstica, não um artigo "pronto para publicação".

**Artigo de submissão (R410–R412):** [ARTIGO_RBEP_SUBMISSAO.md](ARTIGO_RBEP_SUBMISSAO.md)
+ [LaTeX/PDF](latex/) — versão **candidata a submissão** com validações
cruzadas agrupadas (LOOCV por país, ML com split por país), controles de
governança (WGI) e estruturais, erros padrão clusterizados por país,
linguagem associativa e proveniência numérica fechada
(`outputs/expanded/provenance_expanded.json`). Nenhuma alegação de Qualis ou
prontidão é feita; aguarda revisão humana e decisão de submissão à RBEP.

**Artigo publicável (R409):** [ARTIGO_PUBLICAVEL.md](ARTIGO_PUBLICAVEL.md) —
versão histórica de 7 países (mantida para auditoria; números preservados).

## Estrutura

```
arm_education_audit/
├── SOURCE_MANIFEST.json        # hashes e imutabilidade dos originais
├── README.md                   # este arquivo
├── RELATORIO_AUDITORIA.md      # achados, severidade, rastreabilidade, gate
├── MANUSCRITO_REVISADO.md      # versão candidata à revisão humana (R408)
├── ARTIGO_PUBLICAVEL.md        # artigo candidato a submissão (R409, 7 países)
├── ARTIGO_RBEP_SUBMISSAO.md    # artigo de submissão RBEP (R410–R412, 135 países)
├── CARTA_AO_EDITOR.md          # carta ao editor (R410, atualizada no R412)
├── data/
│   ├── raw/                    # snapshots originais (R408, 7 países)
│   ├── raw_expandido/          # R412: WDI+WGI country/all + manifest SHA-256
│   └── processed/
│       ├── panel_wdi_1960_2023.csv   # grade 448 país-ano (R408)
│       ├── panel_wdi_expandido_1960_2023.csv  # 8.640 país-ano, 135 países (R412)
│       ├── variable_counts.json      # contagens observadas/ausentes
│       └── data_dictionary.md        # dicionário de dados e regras
├── outputs/
│   ├── reproduction_matrix.csv       # número antigo × refeito × decisão
│   ├── citation_audit.csv            # 33 referências únicas
│   ├── claim_evidence_matrix.csv     # alegação → evidência → limite
│   ├── descritivos_por_pais.csv      # médias 2010–2023 por país
│   ├── associacoes_cluster_robustas.csv  # ρ níveis × primeiras diferenças
│   ├── agent_12_bibliografico/       # auditoria ABNT (reexecução)
│   ├── agent_18_proveniencia/        # proveniência de datasets (reexecução)
│   ├── publishable_tables/           # R409: tabelas 1–6 + JSONs de validação
│   │   ├── tabela1_descr_paises.csv  ├── tabela2_associacoes.csv
│   │   ├── tabela3_loocv.csv         ├── tabela4_subperiodos.csv
│   │   ├── tabela5_painel_efeitos_fixos.csv ├── tabela6_ml.csv
│   │   ├── loocv_folds.json          ├── temporal_blocks.json
│   │   ├── ml_resultados.json        ├── painel_efeitos_fixos.json
│   │   └── provenance.json           # chave → valor (versão 7 países)
│   └── expanded/                     # R412: análise expandida (135 países)
│       ├── tabela1_descr_expandido.csv  ├── tabela2_correlacoes_expandido.csv
│       ├── tabela3_loocv_expandido.csv  ├── tabela4_subperiodos_expandido.csv
│       ├── tabela5_painel_fe_expandido.csv ├── tabela6_ml_expandido.csv
│       ├── loocv_folds_expanded.json
│       └── provenance_expanded.json  # chave → valor (versão 135 países)
├── scripts/
│   ├── collect_wdi.py               # coleta com cache imutável (R408)
│   ├── download_expanded_data.py    # R412: WDI+WGI country/all, cache SHA-256
│   ├── audit_provenance.py          # gates de proveniência
│   ├── analyze_arm_education.py     # descritivos e associações (R408)
│   ├── analyze_publishable.py       # LOOCV, subperíodos, FE, ML (R409)
│   ├── analyze_expanded.py          # R412: painel 135 países + cluster + WGI
│   ├── build_citation_audit.py      # auditoria bibliográfica
│   └── build_source_manifest.py     # manifesto dos originais
└── environment/requirements.txt
```

## Reprodução

```bash
# 1) ambiente
pip install -r environment/requirements.txt

# 2) coletar (ou reutilizar cache; --offline força operação sem rede)
python3 scripts/collect_wdi.py            # online
python3 scripts/collect_wdi.py --offline  # a partir do cache

# 3) análise
python3 scripts/analyze_arm_education.py
python3 scripts/analyze_publishable.py    # gera publishable_tables/ (R409)

# 4) auditoria bibliográfica e manifesto
python3 scripts/build_citation_audit.py
python3 scripts/build_source_manifest.py

# 5) testes TDD (RED antes dos scripts; agora GREEN)
python3 -m pytest tests/test_r408_arm_article_audit.py -v
python3 -m pytest tests/test_r409_artigo_publicavel.py -v
python3 -m pytest tests/test_r410_artigo_rbep.py -v
```

## Versão de submissão (R410)

- `ARTIGO_RBEP_SUBMISSAO.md` — manuscrito adequado às normas da **RBEP/INEP**
  (título PT/EN/ES; resumo/abstract/resumen; palavras-chave Brased 3–5 por
  idioma; citações ABNT NBR 10520 caixa alta; 16 referências ABNT NBR 6023;
  corpo sem avisos editoriais; números idênticos ao R409).
- `CARTA_AO_EDITOR.md` — carta de submissão com ciência aberta e declarações
  (ineditismo, conflitos, autoria); é aqui que ficam os avisos de candidatura.
- `latex/ARTIGO_RBEP_SUBMISSAO.tex` — fonte LaTeX (pdflatex, A4, 12pt,
  margens ABNT 3/3/2/2 cm, espaçamento 1,5, newtxtext, 6 tabelas booktabs).
- `latex/ARTIGO_RBEP_SUBMISSAO.pdf` — PDF compilado (11 páginas A4).
- Norma: Revista Brasileira de Estudos Pedagógicos (INEP), Qualis A1 em
  Educação (quadriênios 2017–2020 e 2021–2024), e-ISSN 2176-6681.

## Compilar o LaTeX (R411)

```bash
cd latex
pdflatex ARTIGO_RBEP_SUBMISSAO.tex   # duas passadas
```

## Regras invioláveis

- Os originais em `/mnt/c/Users/marce/Downloads/` são **somente leitura**
  (hashes em `SOURCE_MANIFEST.json`).
- A ficha do *Médico Virtual Supremo v4* é um **protótipo/PoC** e **não
  valida** o artigo econômico.
- Resultados sem código/dados originais são classificados como **não
  reproduzidos**; nenhum número foi ajustado para coincidir.
- O snapshot WDI (12/08/2026) não é descrito como idêntico ao estado da API
  em 17/03/2026 citado no manuscrito.
- Nenhuma saída é denominada "Qualis A1", "validada" ou "pronta para
  publicação" sem revisão humana/por pares.

## Limites

Com 7 clusters nacionais, a inferência é frágil; associações em níveis são
vulneráveis a tendência; o painel cobre apenas indicadores WDI (PISA e
Barro–Lee não entraram por falta de fonte oficial com hash). Publicação segue
bloqueada conforme o gate do relatório.
