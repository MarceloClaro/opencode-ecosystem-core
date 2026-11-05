# R1069 — Centro de Produção Global, atenção executiva e adaptação externa

**Status:** implementado e testado. Archify e image-story estão instalados
externamente; os demais adaptadores têm gates explícitos. Nenhum vídeo foi
renderizado, nenhuma conta foi autenticada e nada foi publicado.

## 1. O que mudou no Core

| Arquivo | Função |
|---|---|
| `transformer/executive.py` | Atenção executiva com oito cabeças: objetivo, estágio, evidência, risco, confiança, orçamento, progresso e tags. |
| `marceloclaro/production_center.py` | Centro de Produção Global com estágios, orçamento, consentimento, evidência e recibo. |
| `integrations/external_skills.py` | Registro de adaptadores externos, `status`, `plan` e `probe` REA limitado. |
| `marceloclaro/orchestrator.py` | Método `production_center_action` para `status`, `plan` e `run`. |
| `integrations/ecosystem_mcp.py` | Ferramenta MCP `ecosystem_production`. |
| `.opencode/skills/producao-global/SKILL.md` | Interface `/producao` e política de gates. |
| `tests/test_r1069_production_center.py` | Testes da atenção, do centro, do registro e do MCP. |

## 2. Execução real do centro

Objetivo: `produzir um diagrama da arquitetura do Core`.

```text
specify → route → execute:archify → verify → reflect → deliver
status=completed; stage=complete; selected_adapter=archify
confidence_promoted=false; external_validation=false
```

O plano do Archify é um **handoff de skill** com `argv` seguro para `doctor`;
o centro não renderiza nem executa o pacote de terceiro. O recibo preserva
licença, commit (quando houver), gates e limitações.

A cabeça `tags` normaliza acentos e evita o falso positivo lexical: para
`produzir um vídeo de animação com p5`, o centro seleciona
`opus-video-skills`; para `produzir um diagrama da arquitetura do Core`,
seleciona `archify`; para `criar uma história em imagens com narração`,
seleciona `image-story-video-wizard`. Com `--safe-checks`, o `archify doctor`
e o `project_state.py --help` executam e retornam `returncode=0`; render, OAuth
e coletor seguem bloqueados.

## 3. Evidência REA

O REA 6.8.0 foi usado em escopo reduzido (`--detail summary`,
`--source-path`, `--evidence_output`), com cache fora do repositório:

| Adaptador | Evidence ID | Subject SHA-256 | Cobertura |
|---|---|---|---|
| `archify` | `ev_fa03d9b1...` | `d10a2ac221...` | 124/124 |
| `distilly` | `ev_0125c5c9...` | `6331ebf421...` | 10/10 |
| `opus-video-skills` | `ev_27db9cd9...` | `49ffcd1157...` | 33/33 |
| `reel-video` | `ev_8587b726...` | `b2a0a8346f...` | 22/22 |

O Archify completo via MCP excedeu o orçamento de 10 MiB e foi rejeitado com
`resource_constraint`; a análise CLI em escopo reduzido concluiu e gravou a
evidência. Isso é um limite do transporte, não uma falha silenciosa.

## 4. Adaptação dos externos

| Item | Estado | Decisão |
|---|---|---|
| `archify` | Apache-2.0; `doctor` 27/27; smoke test 827 KB | Instalado e adaptado. |
| `image-story-video-wizard` | MIT; 9 testes; estado `VALID` | Instalado em `~/.agents/skills/image-story-video-wizard` e carregado. |
| `opus-video-skills` | MIT; Chromium Playwright encontrado; ffmpeg presente | Pronto; nenhuma instalação extra de Chrome necessária. |
| `kdense-scientific-agent-skills` | MIT; 177 SKILL.md | Já integrado; commit local = HEAD. |
| `hbg-life-simulation` | MIT; 10 `.mjs` válidos; estilo 1920×1080 | Parcialmente destravado: `hyperframes` e `media-use` instalados do upstream Apache-2.0; ainda faltam `code-video-visual-qa` e `imagegen`; proxy local não configurado. |
| `reel-video` | MIT; CLI/review board | Bloqueado: `grok` e `codex` ausentes; decisão adiada. |
| `distilly` | MIT; 40 testes rápidos | Gate de consentimento/privacidade; nenhum perfil criado. |
| OpenDesign / Paperclip | Apache-2.0 / MIT | Mantidos fora do Core. |

### Decisão sobre o `hbg-life-simulation`

Decisão:

- `hyperframes`, `hyperframes-cli`, `hyperframes-registry` e `media-use` foram
  instalados externamente pelo CLI oficial do HyperFrames 0.9.15
  (Apache-2.0), sem copiar o OpenMontage AGPL.
- Não instalar `imagegen` nem `code-video-visual-qa` a partir de clones não
  oficiais: o hbg espera o caminho de sistema do Codex
  (`~/.codex/skills/.system/imagegen`) e não há fonte oficial verificada.
- O proxy local exige OAuth e consentimento por projeto; não foi iniciado.
- O pipeline é chinês e usa GSAP via CDN.
- `media-use` recebeu alerta Socket/Snyk no instalador; permanece externo e
  não foi executado.

O adaptador permanece no registro como `blocked`, com a lista exata de
dependências. Nada foi executado além do check read-only `ready`.

## 5. Eficiência e autonomia

- **Sem cópia de terceiros**: os adaptadores apontam para o diretório externo e
  preparam handoff, argv e gates.
- **REA sob demanda**: `status` não chama REA; `probe` usa escopo reduzido,
  timeout e cache, com hash da evidência.
- **Orçamento**: o centro limita passos e custo; esgotou, para.
- **Checagem segura**: `--safe-checks` executa apenas o `safe_argv` read-only
  declarado (ex.: `archify doctor`), com timeout e sem shell; o resultado entra
  na evidência. Render, OAuth, coletor e workspace-write continuam fora.
- **Consentimento**: `hbg`, `reel` e `distilly` devolvem `awaiting_consent` sem
  inventar autorização.
- **Metacognição**: cada passo registra ação, estágio, resultado e lição; o
  recibo nunca promove confiança (`confidence_promoted=false`).
- **Atenção executiva**: a decisão é explicável por cabeça e por gate, não uma
  caixa-preta; a cabeça `tags` usa palavras-chave normalizadas sem acentos e
  separa, por exemplo, Archify (diagrama) de opus-video-skills (vídeo/p5).

## 6. Testes

```text
tests/test_r1069_production_center.py
tests/test_r640_ecosystem_surface.py
tests/test_transformer.py
tests/test_r212_attention_blackboard.py
tests/test_r640_autonomous.py
tests/test_r644_autonomous_health.py
tests/test_r886_metacognitive_loop.py
tests/test_r1050_metacognitive_gate.py
tests/test_metacognitive_superhuman.py
99 passed
```

## 7. Limites

- A atenção é heurística determinística; não é rede neural treinada.
- `run` não renderiza, não abre OAuth, não chama coletor e não executa código
  de terceiro.
- Nenhum Chrome Google foi instalado; foi usado o Chromium já presente no cache
  Playwright (`~/.cache/ms-playwright/chromium-1252/chrome-linux64/chrome`).
- Nenhuma conta, cookie, token ou credencial foi lida.
- Nenhuma validação externa, publicação ou promoção de confiança.

## 8. Próximo passo

1. Reiniciar/reconectar o OpenCode para carregar `ecosystem_production` e a
   skill `producao-global`.
2. Usar `/producao plan` e `--safe-checks` antes de qualquer produção externa.
3. Para o `hbg`, ainda faltam `imagegen` e `code-video-visual-qa`; não instalar
   clones não oficiais. O proxy local continua exigindo OAuth/consentimento.
4. Para o `reel-video`, decidir se `grok`/`codex` serão instalados e
   autenticados.
