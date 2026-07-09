# SPEC: Pipeline de Orquestração AutoEvolve para LaTeX

## 1. Visão Geral

O pipeline AutoEvolve para LaTeX é um sistema autônomo que detecta, diagnostica
e corrige problemas de qualidade em documentos acadêmicos LaTeX (padrão ABNT),
utilizando TDD como quality-gate.

**Princípio**: *TDD First — Primeiro os testes, depois o código de refino.*
O orquestrador executa as suites TDD; se houver falha, aplica correção seletiva;
re-executa TDD até passagem completa; registra aprendizagem.

**Menu Adaptativo**: O `menu.py` substitui scripts manuais por um painel que
auto-descobre artefatos (`.tex`, testes, pipelines, backups, insights) e
constrói menu dinâmico com 6 categorias, plugin system via `.menu_registry.json`,
e 4 modos de execução (interativo, direto, lista, diagnóstico).

**Framework de referência**: `orchestration/FRAMEWORK.md` (documento conceitual).

---

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoEvolve Orchestrator                   │
│              orchestration/refinement_loop.py                │
├─────────────────────────────────────────────────────────────┤
│  SENSE ─► DIAGNOSE ─► FIX ─► VERIFY ─► EVOLVE ─► LEARN     │
└─────────────────────────────────────────────────────────────┘
         │           │         │          │          │
         ▼           ▼         ▼          ▼          ▼
    [.tex/.log]   [parser]  [backup/   [TDD       [memory/
                   (regex)   writer]    suites]    history]
```

### 2.1 Componentes

| Módulo | Localização | Função |
|--------|-------------|--------|
| **TDD Runner** | `tests/run_all_tests.py` | Compila (2 passes), executa 3 suites, gera relatório JSON |
| **Compilation Gate** | `tests/test_compile.py` | 5 testes: exit code, erros, undefined refs, PDF, cross-ref finality |
| **Structure Gate** | `tests/test_structure.py` | 6 testes: seções ABNT, labels, label-ref, numeração manual, figuras, newpage |
| **Quality Gate** | `tests/test_quality.py` | 5 testes: overfull < 12pt, overfull ≤ 8, underfull < 10000, widows/orphans, font warnings |
| **Orchestrator** | `orchestration/refinement_loop.py` | Pipeline completo SENSE→LEARN |
| **Fix History** | `orchestration/fix_history.json` | Histórico de correções entre sessões |
| **Backups** | `orchestration/backups/` | Backups pré-correção com timestamp |

---

## 3. Pipeline (6 estágios)

### 3.1 SENSE
- Lê o arquivo `.tex` e compila (2 passes)
- Extrai métricas: páginas, tamanho PDF
- Verifica integridade do diretório

### 3.2 DIAGNOSE
- Parseia `artigo_150_questoes.log` com regex:
  - `! LaTeX Error:` — erros fatais
  - `Overfull \hbox` — overfull boxes (com badness e dimensão)
  - `Underfull \hbox` — underfull boxes (com badness)
  - `LaTeX Warning:.*undefined` — referências/citations indefinidas
  - `LaTeX Font Warning:` — warnings de fonte
- Classifica gravidade: ERROR > OVERFULL > UNDERFULL > FONT

### 3.3 FIX
- Backup automático: copia `.tex` para `backups/` com timestamp
- Overfull < 3pt: insere `\sloppy` localmente via ambiente `\begin{sloppypar}...\end{sloppypar}`
- Overfull ≥ 3pt (cosmético): encurtamento textual estratégico (ver seção 5)
- Underfull em `p{}` colunas: substitui colunas justificadas por `>{\raggedright\arraybackslash}`
- Underfull em texto corrido: insere `\looseness=-1` ou `\sloppy` seletivo
- Undefined refs: recompila com 2 passes (resolve por processamento sequencial)

### 3.4 VERIFY (Quality Gate)
- Executa `run_all_tests.py`
- Se PASS: prossegue
- Se FAIL: re-entra no loop DIAGNOSE→FIX (máximo 5 iterações)

### 3.5 EVOLVE
- Registra sessão em `fix_history.json`:
  - Timestamp, hash do arquivo, problemas encontrados, correções, resultado
  - Detecta padrões: recorrência de overfull, underfull persistente
- Atualiza contagem de padrões de correção utilizados

### 3.6 LEARN
- Gera insights: tendências (issues crescentes/decrescentes), padrões mais frequentes
- Monitora estabilidade de página
- Salva em `orchestration/fix_history.json`

---

## 4. Quality Gates (TDD Suites)

### 4.1 Compilation Gate (`test_compile.py`)
| # | Teste | Critério | Falha se |
|---|-------|----------|----------|
| 1 | Exit code | `pdflatex` retorna 0 | exit code ≠ 0 |
| 2 | LaTeX errors | `egrep '^!'` vazio | qualquer erro LaTeX |
| 3 | Undefined refs | `egrep 'undefined'` vazio | ref/citation sem definição |
| 4 | PDF size | arquivo > 100 KB | PDF ausente ou < 100 KB |
| 5 | Cross-ref finality | "Rerun" warnings vazios | labels não estabilizados |

### 4.2 Structure Gate (`test_structure.py`)
| # | Teste | Critério | Falha se |
|---|-------|----------|----------|
| 1 | ABNT sections | `\section{introdução}`, `\section{considerações finais}` | seções obrigatórias ausentes |
| 2 | Required labels | `\label{introdução}`, `\label{metodologia}`, etc. | labels obrigatórios ausentes |
| 3 | Label-ref balance | cada `\label` referenciado por ≥1 `\ref` | label órfã |
| 4 | No manual numbering | `\section{1.}` proibido | numeração manual detectada |
| 5 | Figure files exist | arquivos em `\includegraphics` existem | figura ausente |
| 6 | `\newpage` discipline | `\newpage` antes de `\section{` | newpage faltante |

### 4.3 Quality Gate (`test_quality.py`)
| # | Teste | Critério | Falha se |
|---|-------|----------|----------|
| 1 | Overfull severity | todas < 12.0pt | overfull ≥ 12pt |
| 2 | Overfull count | ≤ 8 | > 8 overfull boxes |
| 3 | Underfull badness | todas < 10000 | underfull badness ≥ 10000 |
| 4 | Widow/orphan lines | `\clubpenalty` ou `\widowpenalty` configurados | sem proteção ou detectado |
| 5 | Font warnings | log sem font warnings | font warning presente |

---

## 5. Estratégias de Correção (FIX)

### 5.1 Overfull < 3pt (cosmético automático)
```latex
\begin{sloppypar}
% parágrafo com overfull
\end{sloppypar}
```
O orquestrador insere automaticamente quando `auto_fixable = True`.

### 5.2 Overfull ≥ 3pt (encurtamento textual manual)
Overfulls maiores exigem intervenção guiada. Estratégias eficazes:

| Estratégia | Exemplo | Ganho típico |
|------------|---------|--------------|
| Remover advérbios/sinônimos | "domina amplamente" → "predomina" | 10-15pt |
| Simplificar conectivos | "enquanto que" → "e" | 4-8pt |
| Remover redundância | "questões" após "questões objetivas" | ~6pt |
| Contrair expressões | "construiu-se uma" → "construiu-se" | 4-6pt |
| Trocar verbo longo | "apontou" → "indicou" | ~2pt |
| Abreviar título inglês | "Comparative Analysis between" → "Comparing" | ~10pt |

**Regra prática**: Overfull > 3pt → encurtar texto; Overfull ≤ 3pt → `\sloppy` wrapper.

### 5.3 Underfull em tabelas
- **Causa**: colunas `p{width}` com texto curto justificado.
  Palavras hifenizadas curtas em coluna estreita produzem subpreenchimento.
- **Correção**: `>{\raggedright\arraybackslash}p{width}` para colunas textuais curtas;
  `c` ou `l` para colunas numéricas.

### 5.4 Underfull em texto corrido
- **Causa**: parágrafo muito curto na última linha
- **Correção**: `\looseness=-1` (remove uma linha) ou `\sloppy` local

### 5.5 Undefined References
- **Causa**: compilação incompleta (1 pass)
- **Correção**: recompilar com 2+ passes

---

## 6. Ciclo de Vida

### 6.1 Menu Adaptativo (`menu.py`)

O painel central de operação do ecossistema é o **menu adaptativo**,
que substitui scripts manuais por uma interface dinâmica que se
auto-configura para qualquer projeto LaTeX.

**Princípio**: *One menu to operate, reproduce, register, audit — any project.*

#### Arquitetura

```
menu.py
├── DiscoveryEngine        — varre diretório: .tex, tests/, orchestration/, backups/
├── MenuActionBuilder      — constrói ações a partir dos artefatos descobertos
├── MenuRenderer           — renderiza menu categorizado + plugins
└── RunnerEngine           — executa ação selecionada
```

#### Categorias Dinâmicas

| Categoria | Origem | Exemplo de Itens |
|-----------|--------|------------------|
| **OPERACIONAR** | Descoberta + registry | Compilar, testar, pipeline, utilitários |
| **REPRODUZIR** | Backups encontrados | Restaurar backup específico |
| **REGISTRAR** | Fixos | Registrar correção, gerar relatório |
| **AUDITAR** | Fixos + dinâmicos | Histórico, métricas, dependências |
| **APRENDER** | Insights + registry | Explorar evoluções, abrir documentação |
| **FERRAMENTAS** | Registry apenas | Utilitários registrados pelo usuário |

#### Modos de Execução

| Comando | Modo | Descrição |
|---------|------|-----------|
| `python menu.py` | Interativo | Menu colorido com navegação numérica |
| `python menu.py <n>` | Direto | Executa opção N sem menu |
| `python menu.py --list` | Listagem | Exibe todos os artefatos descobertos |
| `python menu.py --quick` | Diagnóstico | Executa TDD, exibe métricas, sai |

#### Plugin System (`.menu_registry.json`)

Comandos externos registram-se via JSON no diretório raiz do projeto:

```json
{
  "commands": [
    {
      "id": "meu-comando",
      "name": "Nome visível no menu",
      "description": "Descrição curta",
      "category": "FERRAMENTAS",
      "command": ["cmd", "/c", "type", "arquivo.txt"],
      "cwd": ".",
      "timeout": 30
    }
  ]
}
```

- Categorias válidas: `OPERACIONAR`, `REPRODUZIR`, `REGISTRAR`, `AUDITAR`, `APRENDER`, `FERRAMENTAS`
- Comandos aparecem automaticamente na numeração do menu
- Sem edição de `menu.py` necessária

#### Auto-Descoberta de Artefatos

O `DiscoveryEngine` identifica automaticamente:

- **.tex**: arquivos LaTeX no diretório raiz (tamanho, páginas estimadas)
- **Testes**: `tests/test_*.py`, com descrição extraída de docstrings
- **Pipelines**: `orchestration/*.py` com nomes sugestivos
- **Backups**: `orchestration/backups/*.tex` ordenados por data
- **Insights**: `orchestration/evolutions/*.md`
- **Registrados**: Comandos de `.menu_registry.json`

### 6.2 Execução Manual Tradicional
```bash
# Executar todas as suites TDD
python tests/run_all_tests.py

# Executar loop de refino completo
python orchestration/refinement_loop.py
```

### 6.3 Execução CI (planejado)
- Gatilho: push para `artigo/artigo_150_questoes.tex`
- Pipeline: compilar → TDD → loop → relatório
- Artefato: relatório JSON + PDF

---

## 7. Decisões Arquiteturais (ADRs)

### ADR-001: TDD como quality-gate, não apenas teste
*Contexto*: Precisamos garantir que correções não degradem qualidade.
*Decisão*: TDD é gate de qualidade. Bloqueia avanço se testes falharem.
*Consequência*: Correções são sempre validadas antes de serem aceitas.

### ADR-002: Backup antes de qualquer correção
*Contexto*: Loop de refino pode corromper o documento.
*Decisão*: Backup automático em `orchestration/backups/` com timestamp.
*Consequência*: Zero perda de dados. Rollback trivial.

### ADR-003: Parsing de log via regex, não AST
*Contexto*: LaTeX não possui AST padronizado.
*Decisão*: Regex sobre `.log` para diagnosticar problemas.
*Consequência*: Precisão limitada a padrões conhecidos; cobertura ~90%.

### ADR-004: Limite de 5 iterações no loop
*Contexto*: Loop infinito pode ocorrer se correção não resolve o problema.
*Decisão*: Máximo 5 iterações FIX→VERIFY. Após, relatório manual.
*Consequência*: Evita loops infinitos. Garante terminabilidade.

### ADR-005: Uma correção por iteração
*Contexto*: Múltiplas correções simultâneas dificultam rastreamento.
*Decisão*: Uma auto-fix por iteração; loop repete até todas resolvidas.
*Consequência*: Cada fix é isolado e auditável.

### ADR-006: Menu adaptativo em vez de estático com opções fixas
*Contexto*: Menu com 11 opções hardcoded quebrava se arquivos mudassem de nome ou diretório.
*Decisão*: Menu com `DiscoveryEngine` que varre diretório, descobre artefatos e constrói menu
dinamicamente. Plugin system via `.menu_registry.json` para comandos customizados.
*Consequência*: Funciona em qualquer projeto LaTeX sem edição manual. Números de opções
variam conforme descoberta.

---

## 8. Histórico de Execuções

| Data | Iterações | Resultado | Principais Correções |
|------|-----------|-----------|---------------------|
| 2026-05-28 (10:13) | 1 | PASS (16/16) | Documento limpo — 0 issues |
| 2026-05-28 (08:53) | 1 | PASS (16/16) | longtable: colunas `p{4.2cm}` → `>{\raggedright\arraybackslash}p{4.2cm}`; colunas numéricas → `c`/`l` |
| 2026-05-28 (08:42) | 1 | PASS (15/16) | Preliminar — underfull na longtable (não resolvido) |
| 2026-05-28 (17:52) | — | — | Menu adaptativo — `menu.py` reescrito: auto-descoberta, 5 categorias, plugin system `.menu_registry.json` |

---

## 9. Métricas

| Métrica | Valor |
|---------|-------|
| Qualidade alvo | 16/16 testes passando (100%) |
| Qualidade atual | 16/16 |
| Overfull boxes | **0** (era 4, máximo 11,7pt) |
| Underfull boxes | **0** (era 1, badness 10000) |
| Erros LaTeX | 0 |
| Font warnings | 0 |
| Páginas | 24 |
| Sessões de execução | 4 |
| Padrões de correção conhecidos | 3 (sloppy wrapper, text shortening, raggedright column) |
| Modos de operação | 4 (interativo, direto, lista, diagnóstico) |
| Plugin commands registrados | 5 (documentação, contagem, limpeza) |
