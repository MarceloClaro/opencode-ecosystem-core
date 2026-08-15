# SPEC-935-R420 — Apêndice A: Glossário de símbolos, códigos e abreviaturas

## Objetivo

Adicionar ao manuscrito `ARTIGO_RBEP_SUBMISSAO` um **Apêndice A — Glossário
de símbolos, códigos e abreviaturas**, para facilitar a leitura do artigo
pelo público da RBEP, consolidando: (i) símbolos estatísticos (ρ, Δ, ln,
IC95%, p, n, H0/H1, p.p., D.P.); (ii) códigos oficiais dos indicadores
WDI/WGI usados no painel; e (iii) abreviaturas e siglas técnicas (WDI, WGI,
LOOCV, FE, RF, ROC, GroupKFold, ML, ISO3, P&D, RBEP, SHA-256, UTC).

## Justificativa

- A leitura do manuscrito exige familiaridade com códigos de indicadores
  (ex.: `SE.TER.ENRR`, `NY.GDP.PCAP.KD`) e siglas de método (ex.: LOOCV,
  GroupKFold). O apêndice reduz a barreira de entrada sem poluir o corpo do
  texto.
- O apêndice não altera nenhum resultado nem alegação do artigo; é material
  de apoio, com linguagem neutra e sem termos de overclaim.

## Entregáveis

- Seção **Apêndice A** no MD canônico (`ARTIGO_RBEP_SUBMISSAO.md`), com
  subseções A.1 (símbolos estatísticos), A.2 (códigos de indicadores
  WDI/WGI) e A.3 (abreviaturas).
- Espelho no LaTeX (`latex/ARTIGO_RBEP_SUBMISSAO.tex`), após as Referências,
  dentro das margens (0 Overfull).
- Testes `tests/test_r420_glossario.py` (gate TDD).

## Critérios de aceitação

1. A seção "Apêndice A — Glossário" existe no MD e no TeX.
2. Contém pelo menos: ρ, Δ, ln, IC95%, p, p.p., WDI, WGI, PIB, LOOCV, FE,
   RF, ROC, GroupKFold, ML, ISO3, P&D, `SE.TER.ENRR`, `NY.GDP.PCAP.KD`,
   `NY.GDP.PCAP.KD.ZG`, `SE.XPD.TOTL.GD.ZS`, `GB.XPD.RSDV.GD.ZS`,
   `NV.IND.MANF.ZS`, `SP.URB.TOTL.IN.ZS`, WGI_CC/GE/PV/RQ/RL/VA.
3. Sem termos bloqueados de anti-overclaim no MD e no TeX (texto inteiro):
   "AUC", "percentil", "validado", "validada", "inédito", "inédita",
   "efeito causal", "causalidade", "impulsiona", "leva a", "16,06",
   "0,997", "0.997", "condição necessária".
4. LaTeX compilável; PDF sem Overfull/Underfull.
5. Suíte R408–R420 verde.

## Não escopo

- Não aplicar a q-estatística (Tsallis) nem q-exponenciais ao artigo —
  avaliação conceitual registrada no evo-51 conclui que não há ganho
  inferencial e não há ancoragem teórica no desenho observacional; a
  inferência já é robusta a não-normalidade via erros clusterizados e
  bootstrap por país.
