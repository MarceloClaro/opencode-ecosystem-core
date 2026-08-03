---
spec_id: SPEC-935-R386
title: Restaura contrato dos 9 agentes literários + caminho de relatórios arquivados + aprimoramento cirúrgico de prosa em CONT-01/CONT-02
component: agents/catalog/literary-*.md, projetos/molambudos (fragmentos CONT-01/CONT-02)
status: verified
test_file: tests/test_r385_psychological_immersion_scanners.py (regressão do bug de fronteira de parágrafo), tests/test_r270..r276 (contrato restaurado)
---

# SPEC-935-R386 — Restauração de Contrato + Aprimoramento de Prosa

**Data:** 2026-08-03
**Motivação:** o usuário pediu para prosseguir em sequência com (a) aplicar
os 3 ajustes de maior retorno (interocepção, cruzamento sensorial, comando
direto de 2ª pessoa) em fragmentos específicos de Molambudos, e (b)
corrigir a pendência de infraestrutura achada no diagnóstico R385
(5 suítes de teste quebradas por caminho de relatório movido + 11 agentes
`literary-*.md` com contrato de saída perdido).

## 1. Parte (b) — Infraestrutura

### 1.1 Caminho de relatórios movido

Os relatórios dos ciclos R270-R276 foram movidos, num arquivamento em lote
de 2026-07-30, de `Molambudos_VictoriaRegia/relatorios/` para
`Molambudos_VictoriaRegia/_archive/relatorios/` — junto com outras pastas
`_old`/`backup_*` no mesmo timestamp, confirmando decisão deliberada de
arquivamento, não acidente. Corrigido os **6** testes que ainda apontavam
para o caminho antigo (R270, R271, R273, R274, R275, **e R276**, este
último não fazia parte da lista original de 5 reportada no diagnóstico)
para apontar para `_archive/relatorios/`, respeitando a decisão de
arquivamento em vez de desfazê-la.

### 1.2 Contrato dos 9 agentes literários

11 cards `agents/catalog/literary-*.md` foram recriados por
`scripts/recreate_literary_kdp_agents.py` num commit anterior a esta
sessão (recuperando de uma perda por `git clean -fd`), com um template
genérico que perdeu: `name:` em slug (virou Title Case), `temperature:`,
e todo o texto de contrato de saída/anti-overclaim exigido pelos testes
R272/R275/R276. Corrigido nos 9 cards cobertos por esses testes
(`literary-orchestrator-phd`, `literary-narratology-architect-phd`,
`literary-style-voice-phd`, `literary-character-psychology-phd`,
`literary-symbolic-imagery-phd`, `literary-ethics-trauma-phd`,
`literary-innovation-editorial-phd`, `literary-research-scholar-phd`,
`literary-smoke-minimal`):

- `name:` corrigido para o slug exato (igual ao nome do arquivo) —
  3 desses cards também tinham `agent_id:` interno errado (com "-and-"
  no meio, ex. `literary-style-and-voice-phd`), corrigido também.
- `temperature: 0.2` adicionado (0.1 no `smoke-minimal`, consistente com
  agentes literários irmãos já existentes como `cultural-episteme-agent`).
- `type: literary-agent` / `category: literary` adicionados para
  consistência com o catálogo.
- Nova seção "## Contrato de Saída Obrigatório" em cada card, com o
  schema JSON exigido (`veredito`, `strengths`, `risks`,
  `recommendations`, `safe_claim`, `limites`) e a instrução de nunca
  fabricar profundidade quando o texto for insuficiente ("dados
  insuficientes"), referenciando o(s) scanner(s) Python reais de
  `scanners/literary_scanners.py` (e, quando pertinente, os novos
  `scanners/psychological_immersion_scanners.py` do R385) como piso
  quantitativo objetivo.
- Nova seção "## Guarda Anti-Overclaim" citando os 4 termos exigidos
  (crítica humana, corpus comparativo, validação externa, anti-overclaim).
- `literary-orchestrator-phd` ganhou seção extra sobre detecção de
  retorno vazio de subagente, fallback e consolidação sem declarar
  parecer multiagente falso.
- `literary-research-scholar-phd` ganhou seção extra sobre separação de
  evidência interna vs. externa, exigindo peer review/DOI/ISBN para
  claims de originalidade.

`opencode.json` regenerado via `python3 -m integrations.opencode_cli`
(instrução do `CLAUDE.md` após mudança em `agents/catalog/*.md`) —
corrigiu, como efeito colateral real, 2 falhas pré-existentes não
relacionadas (`test_r137_opencode_config_reproducible.py::
test_opencode_json_commitado_reproduz_o_gerador`,
`test_r212_opencode_permissions.py::
test_build_config_e_identico_ao_opencode_json_apos_geracao`), já que o
`opencode.json` commitado estava desatualizado antes desta sessão.

**Resultado:** 30/30 testes das 7 suítes R270-R276 passam (eram 27
falhas + 3 já passando).

## 2. Parte (a) — Aprimoramento de prosa

Antes de editar, verificado programaticamente: nenhum fragmento
`CONT-*` está travado por hash em `molambudos_r360_reviews.json`,
`molambudos_r361_provenance_drift.json` ou
`molambudos_r362_change_manifest.json` (o conjunto travado é só
`DOC-17`, `LUC-01`, `MEM-06`, `MEM-12`, `MEM-26`, em PT/EN/ZH — já
tratado no R383/R384). CONT-01 e CONT-02 escolhidos como alvo — já
usam boa parte das técnicas, mas mediam baixo em interocepção/cruzamento
sensorial na varredura R385.

Backup manual criado em
`Molambudos_VictoriaRegia/_archive/backup_R386_prosa_edits/` antes de
qualquer edição (mesma disciplina do R383/R384, dado que `projetos/`
não tem histórico git).

**Edições aplicadas** (preservando voz/registro existente — frases
curtas, presente, 2ª pessoa):
- CONT-01: "Seu coração já acelerou antes de você entender por quê."
  (cruzamento olfativo+interoceptivo na mesma cena) e "Sinta o pulso na
  garganta. A respiração ficou mais curta. Não é medo — ainda não. É o
  corpo reconhecendo, antes da mente, que algo mudou." (interocepção +
  comando direto).
- CONT-02: "Sinta o frio subir da nuca até o couro cabeludo. Seu
  estômago se aperta um segundo antes de você lembrar por quê."
  (cruzamento tátil+interoceptivo) e "Não se mexa." (comando direto,
  batida curta antes do clímax do fragmento).

**Medido, não estimado** (scanners antes/depois sobre cada fragmento):

| Fragmento | Scanner | Antes | Depois |
|---|---|---|---|
| CONT-01 | sensory_immersion | 25.56 | 61.06 |
| CONT-01 | hypnotic_induction | 81.25 | 87.5 |
| CONT-02 | sensory_immersion | 25.70 | 45.92 |
| CONT-02 | hypnotic_induction | 37.5 | 61.48 |

`frenetic_pacing` caiu levemente em CONT-01 (62.11→36.99) — as frases
acrescentadas são de comprimento médio, não rajadas curtas; troca-off
esperado entre densidade interoceptiva e fragmentação visceral, registrado
sem esconder.

## 3. Achado e correção de bug real durante a validação

Ao medir o efeito das edições, `psychological_manipulation` não mudou
apesar de duas novas frases imperativas ("Sinta...", "Não se mexa.").
Investigado: `PsychologicalManipulationScanner._evaluate()` procurava
imperativos só após pontuação (`.!?`) ou início absoluto da string —
mas cada parágrafo do LaTeX começa com `\noindent`, não com pontuação,
então um imperativo logo no início de parágrafo nunca era capturado.
Bug sistemático, não específico das minhas edições — provavelmente
subcontava imperativos em todo o corpus. Corrigido: detecção agora
opera por frase (via `_sentences()`), ignorando ruído de marcação
LaTeX (`noindent`, `textit`, `textbf`) no início de cada frase antes de
checar o verbo. Teste de regressão dedicado adicionado. Recontagem no
livro inteiro: `comando_direto_2a_pessoa` sobe de 22 para 28 ocorrências
reais (score 27.56→35.08); `psychological_manipulation` agregado
43.48→45.36.

## 4. Critérios de aceitação

1. 30/30 testes das suítes R270-R276 passam.
2. `opencode.json` reproduz `build_config()` de verdade (2 testes
   pré-existentes corrigidos como efeito colateral honesto, não
   fabricado).
3. Nenhum fragmento `CONT-*` editado quebra cadeia de proveniência
   (nenhum estava travado por hash para começo de conversa — verificado
   programaticamente antes de editar).
4. Edições de prosa preservam voz/registro (frases curtas, 2ª pessoa,
   presente) e são mensuravelmente verificadas (scanner antes/depois),
   não apenas alegadas.
5. Bug de fronteira de parágrafo no scanner de manipulação psicológica
   corrigido com teste de regressão dedicado, sem regressão nos 17
   testes existentes do R385.
6. Zero regressão na suíte completa fora do escopo desta correção
   (34 falhas remanescentes = exatamente as 34 pré-existentes que não
   fazem parte das 30 corrigidas aqui; nenhuma falha nova).
