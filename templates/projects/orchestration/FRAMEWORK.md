# SDD+TDD+AutoEvolve: Framework para Refino Autônomo de Documentos Acadêmicos LaTeX

## 1. Conceito

O framework **SDD+TDD+AutoEvolve** é uma metodologia de engenharia reversa para
garantia de qualidade em documentos acadêmicos LaTeX. Combina três paradigmas:

| Paradigma | Sigla | Função |
|-----------|-------|--------|
| **Spec-Driven Development** | SDD | A qualidade é definida por especificações formais (SPECs) antes da execução |
| **Test-Driven Development** | TDD | Os critérios de qualidade são expressos como testes que falham até serem satisfeitos |
| **AutoEvolve** | — | Loop autônomo que diagnostica, corrige e aprende sem intervenção humana |

O framework é **reutilizável**: pode ser aplicado a qualquer documento `.tex`
que siga o padrão ABNT (ou outro padrão), desde que as SPECs e testes sejam
adaptados.

---

## 2. Filosofia

```
Especificação (SDD) → Testes (TDD) → Execução (AutoEvolve)
       │                    │                  │
       ▼                    ▼                  ▼
  "O que significa    "Como medimos       "Como corrigimos
   qualidade?"         qualidade?"         e aprendemos?"
```

### 2.1 SDD — A qualidade é especificada primeiro
- Documento `SPEC_ORCHESTRATION.md` define o que significa "qualidade".
- Métricas, limites e critérios são explícitos.
- ADRs (Architecture Decision Records) documentam o *porquê* de cada escolha.

### 2.2 TDD — A qualidade é testada objetivamente
- 16 testes em 3 gates (Compilation, Structure, Quality).
- Cada teste tem um critério binário: passa ou falha.
- O documento só é considerado "bom" quando 16/16 passam.

### 2.3 AutoEvolve — A qualidade é mantida autonomamente
- O orquestrador (`refinement_loop.py`) executa o ciclo SENSE→LEARN.
- Correções são tentadas, validadas, registradas.
- O sistema aprende com cada sessão — padrões de correção são acumulados.

---

## 3. Arquitetura Conceitual

```
┌──────────────────────────────────────────────────────────────────┐
│                      SDD Layer (SPEC)                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Compilation │  │   Structure  │  │       Quality          │  │
│  │    Spec     │  │     Spec     │  │        Spec            │  │
│  │ (5 testes)  │  │   (6 testes) │  │    (5 testes)          │  │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬─────────────┘  │
└─────────┼─────────────────┼────────────────────┼────────────────┘
          │                 │                    │
┌─────────┼─────────────────┼────────────────────┼────────────────┐
│         ▼                 ▼                    ▼                 │
│                      TDD Layer (Runner)                          │
│              ┌──────────────────────────┐                        │
│              │    run_all_tests.py      │                        │
│              │  Compila → Testa → Relata │                        │
│              └────────────┬─────────────┘                        │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                           ▼                                      │
│                   AutoEvolve Layer (Orchestrator)                 │
│   ┌──────┐  ┌─────────┐  ┌─────┐  ┌──────┐  ┌───────┐  ┌─────┐ │
│   │SENSE │→ │DIAGNOSE │→ │ FIX │→ │VERIFY│→ │EVOLVE │→ │LEARN│ │
│   └──────┘  └─────────┘  └─────┘  └──────┘  └───────┘  └─────┘ │
│                                                                    │
│   ┌────────────────────────────────────┐                          │
│   │         Memory Layer               │                          │
│   │  ┌──────────────┐ ┌──────────────┐ │                          │
│   │  │fix_history   │ │  backups/    │ │                          │
│   │  └──────────────┘ └──────────────┘ │                          │
│   └────────────────────────────────────┘                          │
│                                                                    │
│   ┌────────────────────────────────────┐                          │
│   │         Menu Layer (Adaptive)      │                          │
│   │  ┌──────────┐ ┌──────────────────┐ │                          │
│   │  │Discovery │ │   Plugin System   │ │                          │
│   │  │ Engine   │ │ .menu_registry.json│ │                          │
│   │  └──────────┘ └──────────────────┘ │                          │
│   │  ┌──────────────────────────────┐  │                          │
│   │  │       Runner Engine          │  │                          │
│   │  │ (interativo/direto/--quick)  │  │                          │
│   │  └──────────────────────────────┘  │                          │
│   └────────────────────────────────────┘                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Quality Gates — Definição Formal

### Gate 1: Compilação
O documento deve compilar sem erros no `pdflatex`.

```
∀ run ∈ {latexmk, pdflatex}: exit_code(run) = 0
∄ line ∈ log: line matches "^!" 
∄ ref ∈ log: ref matches "undefined"
∃ pdf ∈ files: size(pdf) > 100KB
∄ warning ∈ log: warning matches "Rerun"
```

### Gate 2: Estrutura
O documento deve seguir a estrutura ABNT para artigos acadêmicos.

```
∃ section ∈ doc: name(section) = "introdução"
∃ section ∈ doc: name(section) = "considerações finais"
∀ label ∈ doc: ∃ ref ∈ doc: ref references label
∀ section ∈ doc: prefix(section) ∉ {digits}
∀ figure ∈ doc: file(figure) ∈ filesystem
∀ chapter ∈ doc: \newpage before chapter
```

### Gate 3: Qualidade Tipográfica
O documento não deve conter problemas de quebra de linha ou página.

```
∀ overfull ∈ log: dimension(overfull) < 12pt
count(overfull) ≤ 8
∀ underfull ∈ log: badness(underfull) < 10000
∃ penalty ∈ doc: clubpenalty ∨ widowpenalty
∄ font ∈ log: font matches "Font Warning"
```

---

## 5. Catálogo de Estratégias de Correção

### 5.1 Correções Automáticas (executadas pelo orquestrador)

| ID | Padrão | Gatilho | Ação |
|----|--------|---------|------|
| F01 | sloppy wrapper | Overfull < 3pt | Insere `\begin{sloppypar}`...`\end{sloppypar}` |
| F02 | raggedright coluna | Underfull em `p{}` | Substitui `p{width}` por `>{\raggedright\arraybackslash}p{width}` |
| F03 | looseness | Underfull em parágrafo | Insere `\looseness=-1` antes do parágrafo |

### 5.2 Correções Semi-Automáticas (guia para o operador)

| ID | Padrão | Gatilho | Ação |
|----|--------|---------|------|
| F04 | text shortening | Overfull ≥ 3pt | Encurtar texto: remover advérbios, simplificar conectivos, contrair expressões |
| F05 | column type change | Underfull numérico | Trocar `p{width}` por `c` ou `l` |
| F06 | sloppy manual | Underfull persistente | `\sloppy` no preâmbulo ou escopo seletivo |

### 5.3 Correções Manuais (não automatizáveis)

| ID | Padrão | Gatilho | Ação |
|----|--------|---------|------|
| F07 | figure resize | Overfull em figura | `\includegraphics[width=\textwidth]` ou escala |
| F08 | table redesign | Overfull em longtable | Reduzir colunas, mudar landscape |
| F09 | hyphenation | Overfull por palavra longa | `\hyphenation{pa-la-vra}` ou `\-` |
| F10 | language fix | Overfull em inglês | `\selectlanguage{brazil}` para hifenização PT-BR |

---

## 6. Fluxo de Decisão do Orquestrador

```
SENSE: Compilar .tex → obter .log
  │
  ▼
DIAGNOSE: Parsear .log → lista de issues
  │
  ├─ Erros fatais? → ABORTAR (requer intervenção manual)
  │
  ├─ Critical issues? → RELATAR + pular FIX automático
  │
  ├─ Auto-fixable issues? → FIX → VERIFY
  │     │
  │     └─ Passou? → EVOLVE → LEARN
  │     └─ Falhou? → re-DIAGNOSE (max 5x)
  │
  └─ Nenhum issue? → EVOLVE → LEARN (convergência)
```

---

## 7. Métricas de Saúde

| Indicador | Fórmula | Alerta |
|-----------|---------|--------|
| **Cobertura de qualidade** | `testes_passando / 16` | < 1.0 |
| **Densidade de overfull** | `overfulls / páginas` | > 0.33 (8/24) |
| **Severidade máxima** | `max(overfull_pt)` | ≥ 12pt |
| **Estabilidade** | `páginas` constante entre sessões | variação > 0 |
| **Convergência** | `issues_found_sessão_N` | != 0 na 2ª iteração |

---

## 8. Reutilização do Framework

Para aplicar o framework a um novo documento:

### 8.1 Adaptação Mínima
```
1. Copiar tests/, orchestration/ e menu.py para o diretório do .tex
2. (opcional) Ajustar BASE_DIR e TEX_FILE nos scripts .py
3. Executar: python menu.py
```
O menu adaptativo descobre automaticamente `.tex`, `tests/test_*.py`,
`orchestration/*.py`, backups e insights — sem configuração manual.

### 8.2 Adaptação Completa
```
1. Editar SPEC_ORCHESTRATION.md com os critérios específicos
2. Ajustar test_structure.py (seções obrigatórias, labels)
3. Ajustar test_quality.py (limites de overfull/underfull)
4. Executar e iterar
```

### 8.3 Dependências
- `pdflatex` (TeX Live 2023+)
- `Python 3.10+`
- Pacotes LaTeX: `natbib`, `graphicx`, `hyperref`, `longtable`, `booktabs`

---

## 9. Decisões Arquiteturais (ADRs)

As ADRs completas estão em `SPEC_ORCHESTRATION.md` (seção 7). As decisões
fundacionais são:

1. **TDD como gate** — qualidade medida objetivamente por testes, não por inspeção
2. **Backup pré-correção** — segurança contra loops destrutivos
3. **Regex sobre log** — parsing pragmático sem AST LaTeX
4. **5 iterações máx** — garantia de terminabilidade
5. **1 correção/iteração** — rastreabilidade isolada de cada fix
6. **Menu adaptativo** — auto-descoberta de artefatos + plugin system; funciona em qualquer projeto LaTeX sem edição manual

---

## 10. Glossário

| Termo | Definição |
|-------|-----------|
| **Overfull hbox** | Caixa horizontal que excede a largura do texto. Medido em pontos (pt). |
| **Underfull hbox** | Caixa horizontal subpreenchida. Medido em badness (0-10000). |
| **Badness** | Métrica LaTeX de qualidade de quebra: 0 = perfeita, 10000 = péssima. |
| **Quality Gate** | Conjunto de testes que bloqueia o pipeline se não passar. |
| **AutoEvolve** | Capacidade do sistema de se auto-corrigir e registrar aprendizado. |
| **Spec-Driven** | A especificação precede e dirige a implementação. |
| **SDD+TDD** | Especificar primeiro, testar sempre, codificar depois. |
| **Convergência** | Estado onde o loop de refino encontra 0 issues. |

---

## 11. Referências

- `SPEC_ORCHESTRATION.md` — Especificação detalhada do pipeline
- `refinement_loop.py` — Implementação do orquestrador AutoEvolve
- `tests/run_all_tests.py` — Runner TDD
- `tests/test_compile.py` — Compilation Gate (5 testes)
- `tests/test_structure.py` — Structure Gate (6 testes)
- `tests/test_quality.py` — Quality Gate (5 testes)
- `orchestration/fix_history.json` — Histórico de correções
- `orchestration/backups/` — Backups automáticos
- `menu.py` — Menu adaptativo (auto-descoberta + plugin system)
- `.menu_registry.json` — Plugin registry para comandos customizados
