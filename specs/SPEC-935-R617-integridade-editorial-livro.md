# SPEC-935-R617 — Gate de integridade editorial do livro Core

## Problema
Os ciclos R613–R616 introduziram um grande volume de conteúdo editorial no
`livro-core/` (13 seções "Leitura guiada", capítulo de infraestrutura, 46 citações
ABNT) **sem** especificação formal e **sem** testes. Isso viola o Princípio 1 do
Core (SDD/TDD com gate fail-closed): segundo o AGENTS.md, "toda funcionalidade nasce
de uma especificação (specs/SPEC-935-R*.md) e é validada por testes
(tests/test_r*.py)".

O risco concreto é regressão silenciosa. O histórico do lote anterior demonstra
que regressões reais ocorreram e **não foram detectadas**:
- `split()` consumindo o marcador `% ATIVACAO-R613` (15 arquivos afetados, script
  reportou "OK" sem alterar nada);
- macro inexistente `\code{}` (9 ocorrências) quebrando o build;
- `\text{}` sem `amsmath` no preâmbulo;
- label `\label{mod12}` duplicado;
- números de contagem desatualizados em prosa (367/281/254/434 vs. 368/283/256/441).

Cada uma dessas falhas foi encontrada por inspeção manual do orquestrador, não por
gate automático. Este SPEC fecha essa lacuna.

## Escopo
Arquivos de entrada: `livro-core/*.tex`, `livro-core/macros.tex`,
`livro-core/gen_mod10.py`.

## Critérios de aceitação (fail-closed — qualquer violação reprova)

- **AC1 — Marcador R613 íntegro:** todo `mod-*.tex` que contenha
  `\section[Ativação e cálculo]` deve conter **exatamente 1** ocorrência de
  `% ATIVACAO-R613`. Nenhum arquivo pode ter 0 (marcador perdido) ou 2 (geração
  duplicada).
- **AC2 — Labels únicos:** nenhum identificador `elemento{ativ-*}` pode aparecer
  duplicado no conjunto de `mod-*.tex`; nenhum `\label{...}` pode estar
  duplicado.
- **AC3 — Macros existentes:** `\code{` é proibido no livro (a macro real é
  `\cod{`); `\text{` é proibido (não há `amsmath` no preâmbulo; usar `\mathrm{}`).
- **AC4 — Sem boilerplate:** a cadeia "Próximo parágrafo, a citação que ancora"
  não pode existir em nenhum `mod-*.tex` (foi removida em R616).
- **AC5 — Método didático completo:** toda seção
  `\section[Leitura guiada]{Leitura guiada — ...}` deve conter os 7 blocos do
  método Nussenzveig, na ordem: `descricao` (O fenômeno), `definicao`
  (Grandezas), `metodo` (Dedução passo a passo), `resultado` (Exemplo resolvido),
  `aviso` (Limite de validade), `resultado` (Exercícios). Mínimo 6 dos 7.
- **AC6 — Capítulo de infraestrutura não é stub:** `mod-09-infra.tex` deve ter
  ≥ 100 linhas e não pode conter "Em constru" no título do capítulo.
- **AC7 — Contagens coerentes com o repositório:** os números de contagem citados
  no livro (specs, série SPEC-935-R, suítes `test_r*`, ciclos) devem corresponder
  ao que o repositório realmente contém, com margem de tolerância declarada.
- **AC8 —Gerador declarado:** `mod-10-catalogo.tex` deve manter o cabeçalho
  "ARQUIVO GERADO" (protege contra edição manual silenciosa) e `gen_mod10.py`
  deve ser sintaticamente válido e gerar um capítulo com o total de fichas.

## Fora de escopo
Não altera o conteúdo editorial; apenas o fixa em gate. Não valida mérito
científico das afirmações (isso é anti-overclaim, escopo do Módulo 6).

## Verificação
`python3 -m pytest tests/test_r617_livro_integridade.py -q`
