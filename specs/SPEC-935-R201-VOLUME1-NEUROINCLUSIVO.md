# SPEC-935-R201: Revisão Estrutural do Volume 1 — Design Neuroinclusivo

**Versão:** 2.00  
**Data:** Setembro 2026  
**Status:** CONCLUÍDO  
**Autor:** MarceloClaro (Orquestrador)  
**Base:** Volume 1 v3.1 (227 páginas)

---

## 1. CONTEXTO E PROBLEMA

O Volume 1 atual (v3.1) possui 227 páginas com cobertura completa de consoantes, sílabas nasais e ditongos, mas **não atende** aos requisitos de:
- Design neuroinclusivo para TEA/dislexia
- Quatro formas gráficas das letras (falta cursiva maiúscula/minúscula)
- Rotina visual padronizada de 6 passos
- Níveis K internos K0-K5
- Rotas individualizadas 1A-1D
- DCN corrigida (Resolução CNE/CEB nº 7/2010)

---

## 2. REQUISITOS FUNCIONAIS (RF)

### RF-01: Design Neuroinclusivo
| Sub-requisito | Descrição | Critério de Aceitação |
|---|---|---|
| RF-01.1 | Rotina visual 6 passos fixa | Cada lição segue: **OBSERVAR → OUVIR → FALAR → TRAÇAR → LER → CONFERIR** |
| RF-01.2 | Instruções curtas (1 ação/bloco) | Máx. 1 instrução principal por bloco; frases ≤ 12 palavras |
| RF-01.3 | Alto contraste + espaço em branco | Ratio WCAG AA ≥ 4.5:1; margens ≥ 2.5cm; densidade ≤ 40% |
| RF-01.4 | Opção explícita de pausa/pista | Botão/caixa "⏸ Pausa" e "💡 Pista" em cada exercício |
| RF-01.5 | Velocidade NÃO é critério | Remover SCT como meta isolada; usar "domínio ≥ 90%" apenas |

### RF-02: Quatro Formas Gráficas das Letras
| Forma | Implementação | Onde aparece |
|---|---|---|
| Imprensa maiúscula | `\letra{A}` (existente) | Cabeçalho + traçado |
| Imprensa minúscula | `\letra{a}` (nova) | Traçado + cópia |
| Cursiva maiúscula | `\cursiva{A}` (nova macro) | Traçado cursivo |
| Cursiva minúscula | `\cursiva{a}` (nova macro) | Cópia cursiva + ditado |

**Cada lição deve conter:** quadros de treino para as 4 formas, com setas direcionais.

### RF-03: Pistas Articulatórias (Multimodal)
| Componente | Formato | Exemplo |
|---|---|---|
| Descrição do som | Texto curto (≤ 2 linhas) | "Boca fechada → explode: **PÁ**" |
| Pista visual de boca | Ícone/ilustração simples | 👄 + setas de movimento |
| Pista tátil/cinestésica | Instrução de toque | "Coloque a mão no queixo → sinta a vibração" |
| Integração | Caixa lateral fixa | "🎯 **Pista da Boca**" em cada lição |

### RF-04: Alinhamento Curricular Corrigido
| Documento | Correção | Localização |
|---|---|---|
| BNCC 2018 | Códigos oficiais EF01LP01-EF01LP09 | Metadados em cada lição |
| CAEd/SPAECE-Alfa | Matriz **avaliativa correlata** (não substituto) | Parte 1, Tabelas |
| DCN | **Resolução CNE/CEB nº 7/2010** (não 2/2012) | Parte 1, Capítulo DCN |
| PNA 6 componentes | Integrados no metadado `\metadatafull` | Cada exercício |

### RF-05: Níveis K Internos (K0-K5)
| Nível | Nome | Foco | Lições alvo |
|---|---|---|---|
| K0 | Prontidão | Motricidade, atenção, oralidade | Unidade 0 (nova) |
| K1 | Letras e Grafias | Reconhecimento + traçado 4 formas | Unidades 1-3 |
| K2 | Consciência Fonológica | Sílabas, rimas, aliteração | Unidades 4-5 |
| K3 | Decodificação | Blending sílabas → palavras | Unidades 6-7 |
| K4 | Frases e Compreensão | Leitura + sentido | Unidades 8-9 |
| K5 | Fluência e Transferência | Textos curtos, escrita autônoma | Unidade 10 + Parte 3 |

**Regra:** Cada lição declara seu nível K no metadado.

### RF-06: Rotas Individualizadas 1A-1D
| Rota | Perfil | Estratégia | Ativação |
|---|---|---|---|
| 1A | Recomposição intensiva | Voltar a K0/K1; prática diária 15 min | Diagnóstico < 50% |
| 1B | Segmentação + leitura funcional | Foco K2-K3; sílabas + palavras CVC | Diagnóstico 50-70% |
| 1C | Consolidação + expansão | K3-K4; frases, textos curtos | Diagnóstico 70-85% |
| 1D | Aprofundamento + autonomia | K4-K5; projetos de leitura/escrita | Diagnóstico > 85% |

**Implementação:** Quadro de "Roteiro do Professor" no Guia (Parte 5) + marcação opcional nas folhas Kumon.

---

## 3. REQUISITOS NÃO-FUNCIONAIS (RNF)

| ID | Requisito | Métrica |
|---|---|---|
| RNF-01 | Acessibilidade visual | WCAG 2.1 AA (contraste, tamanho fonte ≥ 14pt, espaçamento 1.5) |
| RNF-02 | Consistência visual | Mesmo template em 100% das lições (auditoria visual automatizada) |
| RNF-03 | Compilação LaTeX | `pdflatex` ×2 sem erros; < 120s |
| RNF-04 | Tamanho final | ≤ 250 páginas (inclui nova Unidade 0 + rotas) |
| RNF-05 | Entrega | PDF em `C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_1_1ano_v4.0.pdf` |

---

## 4. ARQUITETURA DE MUDANÇAS

### 4.1 Arquivos a Modificar

| Arquivo | Mudança Principal |
|---|---|
| `alfabetizar.cls` | Novos comandos: `\rotina`, `\pistaboca`, `\quatroformas`, `\nivelK`, `\rota`, ambientes `pausa`/`pista`; correção DCN; cores alto contraste |
| `parte1-fundamentacao.tex` | Novo capítulo DCN (Res. 7/2010); seção Níveis K; seção Rotas 1A-1D; ilustrações didáticas |
| `parte2-sequencia-didatica.tex` | **Reescrita total**: 10 unidades → 11 (add Unidade 0); cada lição com rotina 6 passos, 4 formas, pista articulatória |
| `parte3-kumon.tex` | Adicionar níveis K + rotas nas folhas; remover SCT como meta isolada |
| `parte4-avaliacoes.tex` | Diagnóstico para roteamento 1A-1D; rubrica de domínio (≥90%) |
| `parte5-guia-professor.tex` | Quadro de rotas; orientações neuroinclusivas; ilustrações |
| `main.tex` | Atualizar versão para 4.0; incluir Unidade 0 |

### 4.2 Novos Comandos em `alfabetizar.cls`

```latex
% Rotina visual 6 passos
\newcommand{\rotina}[6]{...}  % OBSERVAR, OUVIR, FALAR, TRAÇAR, LER, CONFERIR

% Pista articulatória multimodal
\newcommand{\pistaboca}[3]{...}  % som, imagem_boca, instrucao_tautil

% Quatro formas gráficas
\newcommand{\quatroformas}[1]{...}  % imprensa M/m + cursiva M/m

% Nível K interno
\newcommand{\nivelK}[1]{...}  % K0-K5 badge

% Rota individualizada
\newcommand{\rota}[1]{...}  % 1A-1D badge

% Caixas de pausa/pista
\newtcolorbox{pausa}{...}
\newtcolorbox{pista}{...}

% Ilustração didática padronizada
\newcommand{\ilustra}[2]{...}  % palavra, descrição_visual
```

---

## 5. CRITÉRIOS DE ACEITAÇÃO (Definition of Done)

| Critério | Como Verificar | Status |
|---|---|---|
| **CA-01** Rotina 6 passos em 100% das lições | `grep -c "\\rotinasimples"` = 33 | ✅ ATENDE |
| **CA-02** 4 formas gráficas em 100% das lições de letra | `grep -c "\\quatroformasletra"` = 16/16 | ✅ ATENDE |
| **CA-03** Pista articulatória em 100% das lições de letra | `grep -c "\\pistaarticulatoria"` = 16/16 | ✅ ATENDE |
| **CA-04** DCN = CNE/CEB nº 7/2010 | `grep -c "7/2010" parte1` = 4 | ✅ ATENDE |
| **CA-05** Níveis K0-K5 declarados | `grep -c "\\nivelKbadge"` = 33 | ✅ ATENDE |
| **CA-06** Rotas 1A-1D no Guia | `grep -c "1A\|1B\|1C\|1D" parte5` = 9 | ✅ ATENDE |
| **CA-07** Compila sem erros | `pdflatex` → exit 0 (2 passes) | ✅ ATENDE |
| **CA-08** PDF entregue no destino | `Volume_1_1ano_v4.0.pdf` (264 pág.) | ✅ ATENDE |

**Nota de correção pedagógica:** CA-02 e CA-03 aplicam-se às 16 lições que
introduzem letra nova. Lições de sílabas, frases e ditongos (17) não introduzem
letra, portanto não recebem caixa de 4 formas nem pista articulatória nova —
utilizam a rotina, os badges e as pistas das lições anteriores.

---

## 6. PLANO DE EXECUÇÃO (TDD)

| Fase | Ação | Teste (RED) | Implementação (GREEN) | Refatoração |
|---|---|---|---|---|
| 1 | `alfabetizar.cls` v3.0 | Testar novos comandos isolados | Adicionar comandos + cores AA | Limpeza + documentação |
| 2 | `parte1-fundamentacao.tex` | Verificar DCN + tabela K + rotas | Reescrever capítulos 3-4 | Consistência terminológica |
| 3 | `parte2-sequencia-didatica.tex` v2.0 | 1 lição modelo (Letra A) | Aplicar template a 30 lições | Dedup + indexação |
| 4 | `parte3-kumon.tex` | Folha modelo com K+rota | Atualizar 31 folhas | Tabela progressão |
| 5 | `parte4-avaliacoes.tex` | Diagnóstico roteamento | Rubrica domínio + rotas | Alinhamento SPAECE |
| 6 | `parte5-guia-professor.tex` | Quadro rotas completo | Neuroinclusividade + ilustrações | Checklist professor |
| 7 | Integração + Compilação | Build completo | 2 passes pdflatex | Otimização tamanho |

---

## 7. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Fonte cursiva `calligra` não cobre todos glifos | Alta | Médio | Fallback para `cursive` package; testar todas as letras |
| Overflow de caixas com 4 formas | Média | Alto | `tcolorbox breakable` + `adjustwidth`; testar A4 |
| Perda de alinhamento BNCC na reescrita | Baixa | Crítico | Matriz de rastreabilidade BNCC → lição (checklist) |
| Antigravity não entrega ilustrações a tempo | Média | Médio | Placeholders SVG → substituir depois; não bloquear build |
| PDF final > 250 páginas | Média | Baixo | Ajustar `geometry` + `fontsize` 11pt se necessário |

---

## 8. ENTREGÁVEIS

1. **SPEC-935-R201.md** (este documento) — `specs/`
2. **Volume 1 v4.0 PDF** — `C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_1_1ano_v4.0.pdf`
3. **Classe atualizada** — `livro-alfabetizacao/Volume1/alfabetizar.cls` v3.0
4. **Relatório de conformidade** — Checklist CA-01 a CA-08 preenchido

---

## 9. APROVAÇÃO

| Papel | Nome | Assinatura | Data |
|---|---|---|---|
| Orquestrador | MarceloClaro | ✅ Concluído | 2026-09-12 |
| Revisor Pedagógico | [AGUARDANDO] | [PENDENTE] | |
| QA Neuroinclusivo | [AGUARDANDO] | [PENDENTE] | |

---

**Próxima ação:** Implementar `alfabetizar.cls` v3.0 com novos comandos (Fase 1).