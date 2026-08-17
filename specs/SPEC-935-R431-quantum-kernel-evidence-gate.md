# SPEC-935-R431 — Geometry-Survival Evidence Gates for Quantum Kernel Applications

## Meta
- **Ciclo**: 249
- **Autor**: Marcelo Claro Laranjeira
- **Status**: CONGELADO (hash `89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf`)
- **Data de corte da literatura**: 2026-08-16

## Objetivo
Produzir artigo acadêmico (MD + LaTeX + PDF + DOCX) que apresenta o framework **Evidence Gate** — regra prospectiva e sequencial de decisão go/no-go para aplicação de kernels quânticos em dados tabulares — e reporta honestamente o resultado negativo de inferioridade estatística do SVM com kernel quântico de fidelidade frente ao SVM-RBF em validação cruzada aninhada repetida.

## Contribuição candidata
**Não** é "primeiro estudo" nem "vantagem quântica". A contribuição é o **Evidence Gate**: regra pré-especificada que integra efeito pareado corrigido, equivalência, sobrevivência geométrica, custo computacional e pares-âncora antes de autorizar avanço a classificador completo em QPU.

## Resultados-chave (dados brutos)
| Métrica | Valor |
|---|---|
| ΔBAC médio (QML − RBF) | −0,217 |
| IC95% corrigido (Nadeau-Bengio) | [−0,285 ; −0,148] |
| p primário corrigido (unilateral H1: Δ>0) | 0,9999 |
| p permutação de sinais (bilateral) | 0,0005 |
| TOST equivalência (margem ±0,02) | p = 0,9999 |
| dz (tamanho de efeito) | −4,495 |
| Classificação | inferioridade estatística neste protocolo |
| Alinhamento kernel-alvo | 0,110 |
| Posto efetivo relativo | 27,9% |
| Sobrevivência statevector→shots→Aer | 100% (BAC estável 0,625) |
| BAC SVM-RBF | 0,875 |
| BAC Reg. Logística | 0,8125 |
| BAC SVM quântico | 0,625 |

## Estrutura do artigo
1. Abstract (≤300 palavras)
2. Introdução (~5.000 chars)
3. Fundamentação Teórica (~4.000 chars)
4. Métodos (~6.000 chars) — Evidence Gate, desenho, kernel, estatística
5. Resultados (~5.000 chars) — primário, escada, multibase, mecanístico
6. Discussão (~6.000 chars) — implicações, limitações, trabalho futuro
7. Conclusões (~2.000 chars)
8. Referências (ABNT)

## Critérios de aceitação
- [ ] ≥40.000 caracteres no corpo (sem referências)
- [ ] Abstract ≤300 palavras, resumo ≤150 palavras
- [ ] Tabela de comparação de modelos com bootstrap IC
- [ ] Tabela de validade statevector→shots→Aer
- [ ] Tabela multi-dataset (suite de aplicações)
- [ ] Resultado negativo reportado sem suavização
- [ ] Nenhuma alegação de "vantagem quântica" ou "primeiro estudo"
- [ ] Evidence Gate formalizado com critérios de go/no-go
- [ ] Referências ABNT consistentes
- [ ] LaTeX compilável
- [ ] Testes ≥15 passando
- [ ] evo-62 + ciclo 249 registrados

## Anti-overclaim
- DIZER: "inferioridade estatística neste protocolo", "não há evidência de superioridade preditiva", "resultado negativo"
- NÃO DIZER: "vantagem quântica", "primeiro estudo", "o kernel quântico supera", "confirma H1"
- O resultado é honesto e restritivo: restringe hipóteses futuras
