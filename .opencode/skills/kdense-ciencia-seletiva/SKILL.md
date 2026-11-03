---
name: kdense-ciencia-seletiva
description: Roteie oito protocolos científicos seletivos — literatura, citação, hipótese,
  delineamento, estatística, poder, peer review e análise exploratória — com gates
  de evidência. Use para estruturação de pesquisa; não importa as 177 skills, não
  executa código de terceiro e não declara validade científica.
metadata:
  round: R1049
  source: https://github.com/K-Dense-AI/scientific-agent-skills
  license: MIT
  adaptation: Seleção e adaptação textual original de 8 protocolos de K-Dense-AI/scientific-agent-skills
    (commit a25cf9ec00e2745d03f8704acf6f6919694ccd9a); sem cópia de scripts ou dependências.
---

# K-Dense seletivo — 8 protocolos

Esta skill é uma **guarda-chuva** para oito protocolos. Ela não instala as 177
skills nem seus scripts. Cada protocolo tem entradas, gates e saída.

| Protocolo | Quando usar | Referência |
|---|---|---|
| Literatura | mapear campo, lacunas e termos de busca | `references/01-literatura.md` |
| Citação | resolver DOI/PMID/arXiv e conferir referência | `references/02-citacao.md` |
| Hipótese | formular hipótese falsificável e rivais | `references/03-hipotese.md` |
| Delineamento | escolher desenho, amostra e controle | `references/04-delineamento.md` |
| Estatística | escolher teste, pressupostos e efeito | `references/05-estatistica.md` |
| Poder | justificar n, detectar mínima diferença relevante | `references/06-poder.md` |
| Peer review | revisar método, evidência e reprodutibilidade | `references/07-peer-review.md` |
| Análise exploratória | gerar pistas, não confirmar hipótese | `references/08-analise-exploratoria.md` |

## Regras

- Cada protocolo produz artefato e status; não há "ciência automática".
- Separe exploratório de confirmatório; não promova hipótese após ver o dado.
- Identificadores e dados devem ter fonte e data.
- Ausência de teste, poder ou dado é limitação declarada, não resultado.
- Nenhum script do repositório original é executado.

## Catálogo completo — 177 skills

Além dos 8 protocolos, o catálogo completo tem 177 skills em 11 categorias.
Use `references` para os protocolos e `CATALOGO.md` + `integrations.kdense_catalog`
para descoberta sob demanda. 168 instruções permissivas estão espelhadas; 9
restritas ficam em `license_hold`, sem cópia local. Nada é auto-carregado ou
executado.

## Limites

Esta skill não copia código, scripts ou hooks do repositório original.

A seleção não cobre as 177 skills, bases pagas ou integrações clínicas. Não
substitui estatístico, bibliotecário, comitê de ética ou revisão por pares.
