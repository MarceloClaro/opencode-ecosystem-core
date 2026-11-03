# Repositórios Claude com skills para vídeo, academia, ciência e programação — R1048

Data da observação: **2026-11-03**. Pesquisa feita pela GitHub REST API e leitura
de README/LICENSE. **Nenhum repositório foi clonado, instalado ou executado.**
Estrelas e descrições são dinâmicas e não substituem auditoria. Catálogo legível
por máquina: [`candidates.json`](candidates.json).

## Método

Consultas usadas: `topic:claude-skills`, `topic:claude-code-skills`,
`"claude skills" video`, `"claude skills" scientific`,
`"claude skills" academic research`, `"scientific reasoning" skill claude`,
`"hypothesis generation" claude skill`, `"peer review" claude skill`,
`"video editing" claude skill ffmpeg`, `remotion skills agent` e
`awesome claude skills`.

Critérios: aderência ao problema, licença, atividade, dependências, risco de
execução, sobreposição com o Core e possibilidade de adaptação sem copiar
código de terceiro. A ordem não é ranking de qualidade.

## Shortlist por frente

### Vídeo, motion e efeitos

| Repositório | Licença | Por que interessa | Recomendação |
|---|---|---|---|
| [win4r/video-director](https://github.com/win4r/video-director) | MIT | Método de direção com gates, `check_timeline.py`, `qa_video.py`, contatos, loudness, silêncio e checagem de frames. Não traz biblioteca de shots. | **Adotar o padrão de QA** e adaptar ao `video-editor-universal`. |
| [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) | MIT | 56 skills em 19 packs: kinetic typography, data animation, explainers, lower thirds, B-roll, Manim e WebGL. | **Selecionar packs** de dados/explainer/lower-third; não instalar os 19. |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | Apache-2.0 | 124 cartões/150 planos, beat sync, sound design e Motion Workbench; usa Remotion. | **Selecionar receitas** para promos; checar assets e NOTICE. |
| [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | MIT | Skill enxuta de motion graphics com loop render → inspecionar frames → corrigir. | **Boa referência** para o gate Remotion; Remotion License continua aplicável. |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Sem LICENSE explícito; Remotion License | Skills oficiais: create, markup, render, captions, maps, docs, license. | **Referência oficial**; não copiar texto sem verificar licença. |
| [0xsline/OpenChatCut](https://github.com/0xsline/OpenChatCut) | AGPL-3.0 | Editor conversacional com timeline, MCP e Remotion. | **Somente referência arquitetural**; AGPL exige decisão jurídica. |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | AGPL-3.0 | 12 pipelines, 100+ ferramentas e 700+ arquivos de skills. | **Somente referência**; superfície e copyleft altos. |

### Pesquisa acadêmica e raciocínio científico

| Repositório | Licença | Por que interessa | Recomendação |
|---|---|---|---|
| [chgagne/claude-skills-research](https://github.com/chgagne/claude-skills-research) | MIT | 10 skills pequenas e sem dependências para revisão de fontes, bibliografia, literatura, comparação de papers, derivações e provas. | **Prioridade alta**: adaptar `reviewing-paper-sources`, `verifying-bibliography`, `verifying-proofs`. |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | 177 skills científicas e 100+ bases; inclui literatura, citação, hipótese, delineamento, estatística, peer review e análise exploratória. | **Selecionar 6–10 skills**; não importar o catálogo inteiro. |
| [K-Dense-AI/claude-skills-mcp](https://github.com/K-Dense-AI/claude-skills-mcp) | Apache-2.0 | MCP de busca vetorial para descobrir skills científicas sob demanda. | **Avaliar depois**; exige embeddings e avaliação de contexto. |
| [panjose/Co-Scientist](https://github.com/panjose/Co-Scientist) | Apache-2.0 | Fluxo file-first para gerar, revisar, ranquear, evoluir e sintetizar hipóteses, com artefatos e validação. | **Avaliar** para o conselho científico; exige validação independente. |
| [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | MIT | Método de pesquisa autônoma em ML, com revisão cruzada e descoberta de ideias. | **Avaliar depois**; loops e experimentos exigem budget/safety. |
| [AlexWortega/ai-peer-review-skill](https://github.com/AlexWortega/ai-peer-review-skill) | MIT | Revisão multiagente com N revisores, meta-review e CSV de preocupações. | **Complemento** ao blind review; diversidade é de uma família de modelo. |
| [Nero1688/claude-academic-skills](https://github.com/Nero1688/claude-academic-skills) | API MIT; README declara mixed/non-commercial | 38 skills para pesquisa quantitativa, qualitativa, causal, revisão e replicação. | **Bloqueado** até reconciliar LICENSE/NOTICE. |
| [KalarisLabs/research-agent-skills](https://github.com/KalarisLabs/research-agent-skills) | API sem licença; README declara MIT | 280+ skills de pesquisa. | **Bloqueado** por inconsistência de licença. |

### Programação avançada e infraestrutura de skills

| Repositório | Licença | Por que interessa | Recomendação |
|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | Metodologia completa: brainstorming, planos, TDD, debugging sistemático, subagentes, revisão e verificação antes de concluir; suporta OpenCode. | **Prioridade alta**: adaptar princípios ao SDD/TDD do Core. |
| [wshobson/agents](https://github.com/wshobson/agents) | MIT | 202 agentes, 185 skills e 105 comandos; rota OpenCode. | **Catálogo de seleção**, não instalação em massa. |
| [anthropics/skills](https://github.com/anthropics/skills) | Mista por skill | `skill-creator`, `mcp-builder`, `webapp-testing`, documentos. | **Padrões oficiais**; checar licença de cada skill. |
| [sno-ai/sno-station-skills](https://github.com/sno-ai/sno-station-skills) | Apache-2.0 | 37 skills de equipe, peer review, handoff e brief. | **Referência**; parte depende de runtime/login externo. |
| [aiwithremy/claude-skills-llm-council](https://github.com/aiwithremy/claude-skills-llm-council) | Sem licença explícita | Conselho de 5 conselheiros com peer review. | **Não copiar**; o Core já tem conselho próprio. |

## O que priorizar no Core

1. **`superpowers` (MIT)** — importar o *método* de TDD, planos pequenos,
   debugging sistemático e verificação antes de concluir. Isso conversa
   diretamente com `sdd/`, `tests/` e o protocolo do orquestrador.
2. **`chgagne/claude-skills-research` (MIT)** — adaptar as skills de revisão de
   fontes, verificação de bibliografia e provas. Baixo custo, sem dependências,
   alto ganho para o pipeline acadêmico e para o conselho científico.
3. **`K-Dense` seletivo (MIT)** — escolher literatura, citação, hipótese,
   delineamento, poder estatístico, análise exploratória e peer review. Não
   instalar as 177 skills.
4. **`motion-skills` + `video-director` + `video-shotcraft`** — primeiro o
   método de QA; depois receitas de motion e planos. O `video-director` é o mais
   alinhado ao princípio “medir o que não se consegue assistir”.
5. **`wshobson/agents` (MIT)** — usar como catálogo de descoberta para agentes de
   engenharia; selecionar poucos e revisar permissões.
6. **`Co-Scientist`/`ARIS`** — avaliar em laboratório isolado, com orçamento,
   limites de execução e revisão humana; não habilitar loops autônomos por
   padrão.

## O que não fazer

- Não instalar milhares de skills: aumenta contexto, superfície de ataque e
  conflitos de instrução.
- Não executar `curl | bash`, hooks, scripts de setup ou MCPs de terceiros sem
  revisão.
- Não copiar código AGPL (OpenChatCut/OpenMontage) para o Core sem decisão
  jurídica.
- Não usar repositório com licença conflitante (Nero1688/KalarisLabs) até
  reconciliar API, LICENSE e README.
- Não tratar estrelas, README ou “validated” como auditoria de segurança,
  qualidade científica ou aceite editorial.

## Protocolo de adoção proposto

1. Fixar repositório, commit e SHA-256 do `SKILL.md`/`LICENSE`.
2. Ler a skill e listar scripts, dependências, rede, credenciais e hooks.
3. Criar uma adaptação local com atribuição, sem copiar conteúdo incompatível.
4. Escrever eval/fixture antes de habilitar; comparar com o comportamento atual.
5. Passar pelo `ecosystem_agent_profile` e pelo Trust Engine; começar com
   permissões mínimas.
6. Registrar no `PROGRESS.md` e no MetaBus; manter receita de reversão.
7. Só declarar ganho após medir em corpus próprio; caso contrário, registrar
   como “referência” ou “não avaliado”.

## Limites

- A pesquisa é uma triagem de repositórios, não uma auditoria de código.
- Licenças foram lidas no README/LICENSE quando disponíveis; divergências foram
  marcadas, não resolvidas.
- Nenhuma skill foi executada; portanto, não há evidência de qualidade,
  segurança ou compatibilidade real com o OpenCode.
- A adoção de qualquer item acima exige decisão explícita e revisão humana.
