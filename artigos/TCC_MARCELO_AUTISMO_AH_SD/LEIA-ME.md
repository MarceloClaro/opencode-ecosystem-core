# TCC — Marcelo Claro Laranjeira

**Título:** Dupla excepcionalidade no Brasil: autismo, altas habilidades/superdotação e desafios de identificação a partir do Censo Escolar (2021–2024)
**Curso:** Pós-graduação Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica — FACUMINAS
**Cidade/ano:** Brasília, 2026.
**Formato:** TCC (monografia), conforme o manual de Metodologia Científica.
**Regra de citação:** literatura científica apenas com **DOI ativo e auditável**; dados oficiais do INEP e legislação como fontes primárias com URL.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `TCC_MARCELO_AUTISMO_AH_SD.pdf` | TCC completo, 40 páginas, A4, 2,5 cm, 1,5, sumário com 55 entradas |
| `TCC_MARCELO_AUTISMO_AH_SD.docx` | Versão editável, Times New Roman 12, 2,5 cm, 1,5 |
| `TCC_CORPO.md` | Corpo textual (introdução, referencial, metodologia, resultados, discussão, conclusão e referências) |
| `TCC_PRETEXTUAL.tex` / `.md` | Capa, folha de rosto, resumo, abstract e lista de abreviaturas |
| `dados/serie_nacional.csv` | Série 2021–2024: TEA, AH/SD, total da educação básica, percentuais e razão |
| `dados/regioes_2024.csv` | Dados regionais de 2024 |
| `dados/estados_2024.csv` | Dados por unidade da federação em 2024 |
| `dados/cenarios.csv` | Cenários exploratórios 2025–2027 |
| `dados/resumo_analise.json` | Resultados consolidados e ajuste linear |
| `dados/doi_audit_final.json` | Auditoria dos 14 DOIs da literatura científica |
| `scripts/analise_dados.py` | Cálculo dos indicadores e cenários |
| `build_tcc.py` | Compilação do PDF e do DOCX |
| `RELATORIO_DADOS.md` | Fontes, extração, cálculos e limitações |
| `RELATORIO_DOI.md` | Auditoria de DOI e exceções |
| `SHA256SUMS.txt` | Hashes dos artefatos |

## Achados principais

- Matrículas de TEA: **294.394 (2021) → 918.877 (2024)**, crescimento de **212%**.
- Matrículas de AH/SD: **23.758 (2021) → 44.171 (2024)**, crescimento de **86%**.
- Razão TEA/AH/SD: **12,4 (2021) → 20,8 (2024)**.
- Região com maior razão: **Nordeste (45,2)**; menor: **Sul (8,0)**.
- Estados extremos: **Ceará (121,8)** e **Paraná (3,9)**.
- Cenário linear 2027: TEA **1.505.807**; AH/SD **65.790**; razão **22,9**.
- Cenário de convergência 2027: TEA **1.223.025**; AH/SD **86.271**; razão **14,2**.

## Estrutura

Capa, folha de rosto, resumo, abstract, lista de abreviaturas, sumário, 1 Introdução, 2 Referencial teórico, 3 Metodologia, 4 Resultados, 5 Discussão, 6 Conclusão e Referências. Não há apêndice.

## Como reconstruir

```bash
cd artigos/TCC_MARCELO_AUTISMO_AH_SD

# 1. Recalcular indicadores e cenários
python3 scripts/analise_dados.py

# 2. Compilar PDF e DOCX
python3 build_tcc.py
```

O PDF é o artefato de referência para paginação e sumário. O DOCX é a versão editável; se a paginação mudar no Word, atualize o sumário.

## Limitações

- O Censo Escolar não cruza TEA e AH/SD; não é possível estimar a prevalência da dupla excepcionalidade.
- As categorias podem se sobrepor; os totais são de matrículas, não de pessoas únicas.
- Em 2021, a categoria aparece como "Autismo"; a partir de 2022, como "Transtorno do Espectro Autista".
- A série tem quatro pontos anuais; os cenários são exploratórios e não são previsões.
- A revisão bibliográfica é narrativa, não sistemática.
- A regra de DOI foi aplicada à literatura científica; as Sinopses do INEP e a legislação são fontes primárias oficiais, com URL.

## Observação

O TCC foi elaborado para Marcelo Claro Laranjeira, no curso de Pós-graduação Lato Sensu da FACUMINAS. A capa e a folha de rosto não incluem linha de orientador(a); se a instituição exigir, basta acrescentar o nome.
