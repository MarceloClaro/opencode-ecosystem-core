# SPEC-935-R1069 — Centro de Produção Global e atenção executiva

**Status:** implementado e testado; nenhuma validação externa ou publicação.
**Objetivo:** ampliar a autonomia e a metacognição do orquestrador com uma
camada de atenção executiva inspirada no Transformer, capaz de decidir o próximo
passo de uma produção e de adaptar skills externas sem copiar código de terceiro.

## 1. Arquitetura

| Componente | Papel |
|---|---|
| `transformer/executive.py` | `ExecutiveAttention`: oito cabeças determinísticas (objetivo, estágio, evidência, risco, confiança, orçamento, progresso e tags), gates rígidos e softmax auditável. |
| `marceloclaro/production_center.py` | `ProductionCenter` + `ProductionStore`: estágios `intake → spec → route → execute → verify → reflect → deliver → complete`; orçamento, consentimento, evidência, histórico, recibo, persistência e retomada. |
| `integrations/external_skills.py` | Registro de adaptadores externos: licença, caminho, entrypoint, dependências, `status`, `plan`, `probe` REA limitado e `safe_argv`. |
| `integrations/video_qa.py` | QA técnico de vídeo com ffprobe/ffmpeg: metadados, black frames, silêncio, loudness e frames. |
| `.opencode/skills/code-video-visual-qa/SKILL.md` | Adaptação Core-native que substitui a dependência homônima do hbg. |
| `skills/imagegen/` | Cliente OpenAI-compatible `generate`/`generate-batch`, compatível com o caminho `.codex` do hbg; chave só no ambiente. |
| `.opencode/skills/imagegen/SKILL.md` | Skill Core-native que expõe o cliente ao catálogo. |
| `MarceloClaroOrchestrator.production_center_action` | Operações `status`, `plan` e `run`, com observação metacognitiva sem promoção de confiança. |
| MCP `ecosystem_production` | Expõe o centro pela rede coordenada. |
| Skill `producao-global` | Interface de comandos e política de gates. |

## 2. Cabeças de atenção

Pesos convexos:

- `goal` 0,10 — alinhamento semântico entre ação e objetivo;
- `stage` 0,20 — ação pertence ao estágio atual;
- `evidence` 0,15 — ganho de evidência;
- `risk` 0,15 — segurança e reversibilidade; o risco do adaptador cai de
  0,65 para 0,30 quando o consentimento já foi dado;
- `confidence` 0,10 — confiança histórica declarada;
- `budget` 0,05 — custo relativo ao orçamento;
- `progress` 0,10 — capacidade de avançar a produção;
- `tags` 0,15 — casamento de palavras-chave do adaptador com o objetivo,
  normalizado sem acentos.

Gates rígidos: indisponibilidade, consentimento ausente, orçamento excedido,
capacidades ausentes e risco alto sem consentimento. A camada é uma heurística
determinística; não é rede neural treinada.

## 3. Ciclo do centro

1. `specify`: cria escopo e critérios de aceitação.
2. `route`: escolhe adaptador/agente elegível.
3. `execute`: prepara o plano do adaptador, sem executar terceiros.
4. `verify`: confere plano, dependências e gates.
5. `reflect`: registra lição e evidência.
6. `deliver`: emite recibo com limitações.

`hbg-life-simulation`, `reel-video` e `distilly` exigem consentimento explícito.
O centro devolve `awaiting_consent` em vez de inventar autorização.

## 4. Adaptadores externos

| Adaptador | Licença | Estado |
|---|---|---|
| `archify` | Apache-2.0 | pronto; instalado em `~/.agents/skills/archify` |
| `imagegen` | Core-native | pronto; cliente OpenAI-compatible, com consentimento por projeto |
| `code-video-visual-qa` | Core-native | pronto; QA técnico com ffprobe/ffmpeg |
| `hyperframes` | Apache-2.0 | pronto; skill oficial instalada |
| `image-story-video-wizard` | MIT | pronto; instalado e carregado |
| `opus-video-skills` | MIT | pronto; Chromium do cache Playwright encontrado |
| `kdense-scientific-agent-skills` | MIT | pronto; catálogo espelhado |
| `hbg-life-simulation` | MIT | **pronto**: `hyperframes`, `media-use`, `code-video-visual-qa` e `imagegen` presentes; CLIProxyAPI autenticado e `readiness: ready` |
| `reel-video` | MIT | pronto com fallback `still-motion`; Grok opcional; Codex opcional para stills |
| `distilly` | MIT | gate de consentimento/privacidade |

Nenhum código de terceiro foi copiado para o repositório. O adaptador aponta
para o diretório externo e prepara um handoff auditável.

## 5. Eficiência

- Registro lazy: `status` só lê caminhos, licença, entrypoint e dependências.
- `plan` não executa; devolve handoff, argv seguro e limitações.
- REA em escopo reduzido: `--detail summary`, `--source-path` e
  `--evidence_output` em cache externo; sem despejar dezenas de MiB no contexto.
- Nenhum shell livre; comandos são listas de argumentos.
- Nenhuma varredura REA no caminho crítico do `status`.
- `allow_safe_checks` executa apenas o `safe_argv` read-only declarado pelo
  adaptador (ex.: `archify doctor`, `project_state.py --help`, `hbg ready`);
  render, OAuth, coletor e workspace-write continuam bloqueados.
- Diagnóstico externo com cache TTL de 15 s: evita repetir git e subprocessos
  de prontidão a cada passo do Centro; `refresh=True` força nova leitura.
- `ProductionStore` grava estado atômico em
  `~/.local/share/opencode-core/productions/` (0700/0600), com `list` e
  `resume`; o histórico não é recriado.

## 6. Aceitação

1. Atenção executiva ranqueia ações e aplica gates de consentimento/orçamento.
2. Centro completa o ciclo com adaptador elegível.
3. Centro para em `awaiting_consent` quando o adaptador exige autorização e
   prefere pedir consentimento ao adaptador mais aderente, em vez de trocá-lo
   silenciosamente por outro.
4. Orçamento limita passos e custo.
5. Registro externo distingue pronto/bloqueado e não executa terceiros.
6. `probe` REA é limitado, grava evidência e devolve hash.
7. `allow_safe_checks` executa somente `safe_argv` read-only e registra o
   resultado; sem `safe_argv`, nada é executado.
8. `code-video-visual-qa` detecta black frames, silêncio, loudness e extrai
   frames de um MP4 local sem executar o alvo.
9. `imagegen` gera uma imagem e um lote por endpoint OpenAI-compatible local,
   rejeita path traversal, exige chave de ambiente e aceita `http` apenas em
   loopback.
10. MCP `ecosystem_production` roteia para o primário e aceita `list`/`resume`.
11. Produção persistida pode ser listada e retomada sem recriar o histórico.
12. Cache de status evita repetir prontidão/git dentro do TTL.
13. Testes verdes.

**Resultado:** **113 passed** em R1069, R640, Transformer, atenção, autonomia,
metacognição, QA de vídeo e imagegen. Execução real do centro com
`hbg-life-simulation`: `specify → route → consent:hbg → execute:hbg → verify →
reflect → deliver`, `readiness=ready` no safe check e
`confidence_promoted=false`; a produção persistida foi listada e retomada sem
recriar o histórico. `imagegen` gerou um PNG 1536×1024 (2,2 MB) em 22,3 s com
`gpt-image-2` pelo CLIProxyAPI local autenticado; a primeira tentativa falhou
com 502 porque o proxy tinha 0 auth entries. O REA analisou `media-use` em
escopo reduzido (75 nós, 18 limitações) e confirmou que ele deve permanecer
externo, não como adaptador padrão.

## 7. Limites

- A atenção é heurística e auditável; não certifica qualidade científica.
- `run` não renderiza vídeo, não abre OAuth, não chama coletor e não executa
  código de terceiro.
- Nenhuma conta, cookie, token ou credencial foi lida.
- Nenhum perfil de pessoa foi criado.
- Nenhuma validação externa ou publicação.
