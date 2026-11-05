# R1067 — Auditoria de fontes externas: design, ciência, orquestração e vídeo

**Status:** auditoria somente leitura. Nenhum repositório foi instalado, copiado
ou executado nesta rodada. Nenhuma validação externa.

## 1. Método

Para cada fonte foram verificados: origem, licença, atividade, linguagem,
tamanho, tipo de artefato (app, skill, lista, CLI), sobreposição com o Core e
risco de execução. Estrelas do GitHub não foram tratadas como prova de
qualidade. Quando a licença não estava clara, a fonte foi classificada como
**referência apenas**.

## 2. Lote 1 — oito URLs

| Fonte | Licença | Tipo | Capacidade real | Decisão |
|---|---|---|---|---|
| `nexu-io/open-design` | Apache-2.0 | App desktop + CLI `od` + MCP | Workspace de design local-first; `od mcp install opencode` | **Externo, sob confirmação**. Não substitui MIRA/OpenMontage. Exige Node ~24 e instalação pesada. |
| `K-Dense-AI/scientific-agent-skills` | MIT | 177 skills | Ciência, bioinformática, química, clínica, dados | **Já integrado** como catálogo espelhado; 177 `SKILL.md`, sem scripts. Commit local `a25cf9ec...` = HEAD upstream; versão 2.72.0. |
| `hesreallyhim/awesome-claude-code` | **CC BY-NC-ND 4.0** | Lista curada | Descoberta de skills/agentes | **Referência apenas**. Não copiar, modificar ou incorporar. A licença proíbe derivados e uso comercial. |
| `titanwings/distilly` | MIT | Meta-skill | Perfis de pessoa a partir de mensagens/documentos | **Não integrar como está**. Exige consentimento, privacidade, direito de uso e limite explícito contra impersonação. |
| `tt-a1i/archify` | Apache-2.0 | Skill + CLI Node | Diagramas HTML interativos: arquitetura, workflow, sequência, ERD, classe, árvore, timeline, waterfall | **Candidato externo**. Instalar via `npx skills` após confirmação; não copiar o pacote para o Core. |
| `paperclipai/paperclip` | MIT | App Node/React | Control plane de agentes, metas, orçamento, rotinas | **Externo**. Duplica a orquestração do Core; avaliar só como dashboard/control plane separado. |
| `MarceloClaro/xianxia-cinematic-video-director` | **Sem licença** | Fork de skill Codex | Storyboard, câmera e continuidade xianxia | **Referência apenas**. Repositório público não concede direito de cópia. O upstream `liyue-aigc/...` também não declara licença. |
| `hesreallyhim/awesome-claude-code` (duplicado) | CC BY-NC-ND 4.0 | Lista | — | Duplicata; mesma decisão. |

### Observações do lote 1

- **K-Dense**: o espelho local tem 168 skills permissivas, 9 em `license_hold`
  com adaptações originais, 177 somente instrução, 0 scripts vendorizados,
  0 autoload. Não há ação pendente; o commit local coincide com o HEAD.
- **Archify**: a skill declara Node `>=18`, licença Apache-2.0 e instalação
  oficial por `npx -y skills@latest add https://archify.si --skill archify
  --agent opencode --global --copy --yes`. O pacote inclui scripts e um
  template de ~787 KB; a instalação deve ser externa e verificada com
  `node <path>/bin/archify.mjs doctor`.
- **OpenDesign**: `package.json` 0.25.1, Node `~24`, pnpm `>=10.33.2`.
  É um app desktop, não uma skill leve. O caminho `od mcp install opencode`
  altera configuração do OpenCode e exige confirmação.
- **Paperclip**: app completo (servidor + UI React). A integração com OpenCode
  é um adaptador entre vários; adotá-lo mudaria o centro de orquestração.
- **Distilly**: o risco não é técnico, é ético. Qualquer adaptação precisa de
  consentimento verificável, minimização de dados, direito de exclusão e
  proibição de simular pessoa real sem autorização.
- **Xianxia**: o README do próprio fork informa que não há licença e que
  “repositório público visível não concede cópia, modificação ou
  redistribuição”. Não deve entrar no Core.

## 3. Lote 2 — Story & Animation (13 repositórios)

| Repositório | Licença | Tipo | Valor para o Core | Decisão |
|---|---|---|---|---|
| `gnipbao/story-to-handdrawn-video` | MIT | Skill Remotion | Vídeo hand-drawn retrato a partir de história/imagem | **Avaliar** como receita Remotion; nicho. |
| `lemomo-ai/lemo-opuscar` | MIT | Prompt library | Curtas cinematográficos e prompts de direção | **Referência**; não copiar a biblioteca inteira. |
| `JohnHeibel/ClaudeAnimationBase` | MIT | Starter p5.js | Animação de personagem com p5.brush → MP4 | **Referência**; útil se houver demanda de p5.js. |
| `aaronyi97/image-story-video-wizard` | MIT | Skill Codex | Vídeo audio-first a partir de tópico, script e imagens | **Avaliar**; bom encaixe com o pipeline de imagem/vídeo. |
| `liyue-aigc/xianxia-cinematic-video-director` | **Sem licença** | Skill Codex | Storyboard/câmera/continuidade xianxia | **Referência apenas**; não copiar. |
| `LetMeHappyCode/auto-video-agent` | **Sem licença** | Agentes Claude Code | SRT → shot list → imagens → vídeo mudo | **Referência apenas**. |
| `tuzhechen2005/opus-video-skills` | MIT | Skills p5.js | Vídeos procedurais em estilos, headless Chrome + ffmpeg | **Avaliar**; complementa Motion Canvas/Remotion. |
| `Mr-funny/hbg-life-simulation` | MIT | Skill HyperFrames | História longa → vídeo narrado com TTS, legendas e QA | **Prioridade alta**; é o mais próximo do stack HyperFrames do Core. |
| `liangdabiao/story-handdrawn-remotion` | **Sem licença** | Skill Remotion | Diário-comic vertical com camadas progressivas | **Referência apenas**. |
| `JimLiu/taohuayuan` | **Sem licença** | Showcase three.js | Cena 3D interativa | **Não é skill**; não integrar. |
| `AsadMoulviDev/reel-video` | MIT | CLI + review board | Ideia → storyboard → keyframes → vídeo curto | **Avaliar** como ferramenta externa de revisão. |
| `AllenAI2014/remotion-guofeng-starter` | MIT | Skill Remotion | Estilo paper-collage chinês a partir de poema/idioma | **Avaliar** se o estilo for necessário; nicho. |
| `taylorzhou16/video-gen` | **Sem licença** | Skill Claude Code | Edição de vlog/música no chat | **Referência apenas**. |

### Leitura do lote 2

O Core já cobre a base: Remotion/Motion Canvas, HyperFrames, MIRA, ffmpeg,
legendas, QA de vídeo, dubbing e edição. O que falta não é “mais um skill de
vídeo”, e sim **receitas específicas**:

1. **HyperFrames + TTS + legendas + QA** — `hbg-life-simulation` é o melhor
   candidato para uma avaliação controlada.
2. **Audio-first image story** — `image-story-video-wizard` cobre um fluxo que
   o Core ainda não tem pronto.
3. **p5.js procedural** — `opus-video-skills` adiciona uma família visual
   diferente de Remotion.
4. **Review board local** — `reel-video` pode complementar a revisão humana,
   mas sobrepõe o editor local.

## 4. Decisão consolidada

### Integrar agora

Nenhum item novo. O K-Dense já está integrado e atualizado.

### Instalar externamente, somente com confirmação

1. **Archify** — skill Apache-2.0, instalação oficial, verificação `doctor`.
2. **OpenDesign** — app Apache-2.0, somente se o usuário quiser um workspace de
   design separado; não substitui MIRA/OpenMontage.
3. **Paperclip** — app MIT, somente se houver necessidade de um control plane
   separado; não substitui o orquestrador do Core.
4. **Distilly** — somente com um contrato de consentimento e privacidade; não
   integrar como skill genérica.

### Avaliação controlada de vídeo

Ordem sugerida: `hbg-life-simulation` → `image-story-video-wizard` →
`opus-video-skills` → `reel-video`. Cada um em diretório externo, com licença
preservada, sem executar scripts de terceiros sem revisão.

### Referência apenas

`awesome-claude-code` (CC BY-NC-ND), `xianxia-cinematic-video-director` e
`liyue-aigc/xianxia...` (sem licença), `auto-video-agent`, `story-handdrawn-remotion`,
`taohuayuan`, `video-gen`, `lemo-opuscar` (biblioteca de prompts) e
`ClaudeAnimationBase` (starter).

## 5. Riscos e limites

- Estrelas e trending não provam qualidade, segurança ou manutenção.
- Skills de terceiros podem conter scripts, dependências e instruções de
  execução; a auditoria não executou nenhum deles.
- Licenças “sem licença” impedem cópia/redistribuição, mesmo com repositório
  público.
- CC BY-NC-ND impede obras derivadas e uso comercial; a lista não pode ser
  incorporada.
- Nenhuma instalação, publicação ou validação externa foi realizada.
- O Core não deve trocar seu orquestrador, Blackboard ou pipeline de vídeo por
  um app externo sem uma decisão arquitetural explícita.

## 6. Próximo passo

Se o usuário autorizar, a ordem de menor risco é:

1. instalar **Archify** externamente e rodar `doctor`;
2. avaliar **hbg-life-simulation** em diretório isolado;
3. avaliar **image-story-video-wizard** em diretório isolado;
4. decidir sobre OpenDesign/Paperclip somente depois de comparar com o
   orquestrador e o editor atuais.

Nenhuma dessas etapas deve copiar conteúdo sem licença para o repositório.
