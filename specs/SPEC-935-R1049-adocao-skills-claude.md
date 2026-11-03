---
spec_id: SPEC-935-R1049
title: Adoção seletiva de skills Claude para SDD/TDD, academia, ciência, motion e QA
component: .opencode/skills + scripts/video_qa.py + research_lab/
status: specified
test_file: tests/test_r1049_skills_adoption.py
depends_on:
  - SPEC-935-R1042
  - SPEC-935-R1046
  - SPEC-935-R1047
  - SPEC-935-R1048
---

# SPEC-935-R1049

## Objetivo

Adotar, de forma seletiva e auditável, padrões dos repositórios triados na R1048:

1. `obra/superpowers` (MIT) — SDD/TDD, planos, debugging e verificação.
2. `chgagne/claude-skills-research` (MIT) — revisão de fontes, bibliografia e provas.
3. `K-Dense-AI/scientific-agent-skills` (MIT) — 8 protocolos científicos.
4. `iart-ai/motion-skills` (MIT) e `win4r/video-director` (MIT) — motion e QA.
5. `Vincentwei1021/video-shotcraft` (Apache-2.0) e `wshobson/agents` (MIT) —
   receitas e catálogo, com seleção.
6. `Co-Scientist`/`ARIS` — laboratório isolado com orçamento e revisão humana.

**Não copiar código de terceiros, não instalar dependências, não executar hooks
ou scripts importados.** A adaptação é textual, original e atribuída.

## Entregáveis

| Frente | Skill local | Conteúdo |
|---|---|---|
| Programação | `superpowers-sdd-tdd` | TDD, planos pequenos, debugging, verificação |
| Academia | `rigor-academico-chgagne` | fontes, bibliografia, provas e derivações |
| Ciência | `kdense-ciencia-seletiva` | 8 protocolos em `references/` |
| Motion | `motion-design-seletivo` | 5 protocolos de motion/data |
| QA de vídeo | `video-director-qa` | gates + `scripts/video_qa.py` |
| Receitas | `video-shotcraft-selecao` | 10 receitas originais em JSON |
| Catálogo | `agentes-engenharia-selecao` | 10 papéis selecionados em JSON |
| Pesquisa | `laboratorio-pesquisa-isolado` | `research_lab/` com budget e manifesto |

## Critérios de aceitação

1. Oito skills novas com frontmatter válido, descrição útil, `metadata.round`,
   `source`, `license` e `adaptation`.
2. Cada skill declara o que **não** faz e não contém instalação automática,
   `curl | bash`, hooks executáveis ou cópia de código-fonte de terceiro.
3. O pacote K-Dense tem exatamente 8 protocolos: literatura, citação, hipótese,
   delineamento, estatística, poder, peer review e análise exploratória.
4. Motion tem 5 protocolos: kinetic typography, data animation, explainer,
   lower thirds e B-roll.
5. `video-shotcraft-selecao` tem 10 receitas originais com fonte, quando usar,
   risco e critério de QA.
6. `agentes-engenharia-selecao` tem 10 papéis, cada um com fonte e licença.
7. `scripts/video_qa.py` inspeciona mídia real: streams, frames, fps, duração,
   loudness, silêncio, frames pretos e contato de frames; retorna código de
   falha em desvio contratual. Teste com vídeo sintético real.
8. `research_lab` é file-first, sem rede, com budget de passos/tempo/custo,
   status explícito, retomada e revisão humana obrigatória; `--dry-run` não
   executa pesquisa.
9. `reports/r1049/sources.json` fixa URL, licença e commit dos repositórios
   usados como referência.
10. Regressão R1033–R1049, `doctor` e guard Remotion verdes; documentação
    atualizada com contagem de skills e limites.

## Não objetivos

- Não instalar as 177 skills K-Dense, os 202 agentes wshobson ou os 56 packs
  motion.
- Não integrar AGPL (OpenChatCut/OpenMontage) nem repositórios com licença
  conflitante (Nero1688/KalarisLabs).
- Não executar LLM, experimento, download ou chamada de rede no laboratório.
- Não declarar qualidade científica, naturalidade, segurança ou paridade com
  editores comerciais a partir de testes técnicos.

## Evidência

- `tests/test_r1049_skills_adoption.py`
- `tests/test_r1049_video_qa.py`
- `tests/test_r1049_research_lab.py`
- `reports/r1049/README.md`
- `reports/r1049/sources.json`
- `reports/r1049/qa-smoke.json`
