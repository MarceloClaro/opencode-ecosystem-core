---
name: producao-global
description: >
  Centro de Produção Global do Core: decide o próximo passo de uma produção
  (especificar, rotear, executar, verificar, refletir, entregar, pedir
  consentimento ou parar) por atenção executiva determinística. Use para
  planejar produções que combinam REA, Archify, image-story-video-wizard,
  hbg-life-simulation, opus-video-skills, reel-video, distilly, K-Dense e
  outras skills externas. NÃO executa código de terceiro, OAuth, render ou
  coletor sem consentimento explícito; o orquestrador marceloclaro permanece
  dono do ciclo SDD/TDD e nenhuma autoavaliação promove confiança.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R1069
spec: SPEC-935-R1069-centro-producao-global.md
---

# Skill: Produção Global (SPEC-935-R1069)

O Centro de Produção Global transforma o orquestrador em uma central de
produção: em vez de apenas escolher um agente, ele pondera o próximo passo por
oito cabeças de atenção — objetivo, estágio, evidência, risco, confiança,
orçamento, progresso e tags — e devolve um recibo auditável.

## Comandos

| Comando | Ação |
|---|---|
| `/producao status` | Mostra estágios, pesos das cabeças e adaptadores externos |
| `/producao adapters` | Lista adaptadores, licenças, dependências e bloqueios |
| `/producao plan '<objetivo>' [--risk low\|medium\|high] [--budget N] [--consent]` | Dry-run: ranqueia ações sem executar |
| `/producao run '<objetivo>' [--risk ...] [--budget N] [--consent] [--safe-checks]` | Ciclo de planejamento/gates; `--safe-checks` roda só checagens read-only declaradas |
| `/producao probe <adapter>` | Análise REA em escopo reduzido, com evidência em cache |

## Uso programático

```bash
python3 -m marceloclaro.production_center status
python3 -m marceloclaro.production_center plan "produzir um vídeo didático com QA"
python3 -m marceloclaro.production_center run "produzir um vídeo didático com QA" --consent
python3 -m integrations.external_skills status
python3 -m integrations.external_skills plan archify --task "diagramar a arquitetura"
python3 -m integrations.external_skills probe distilly --timeout 60
```

No orquestrador:

```python
from marceloclaro.orchestrator import MarceloClaroOrchestrator
core = MarceloClaroOrchestrator(auto_load_agents=False)
core.production_center_action({"operation": "plan", "goal": "produzir um artigo"})
```

## Gates obrigatórios

1. **Licença**: só entram adaptadores com licença verificada e preservada.
2. **Consentimento**: `hbg-life-simulation`, `reel-video` e `distilly` exigem
   autorização explícita; o centro devolve `awaiting_consent`, nunca inventa
   consentimento.
3. **Dependências**: Chrome, ffmpeg, Grok/Codex, proxy local e skills ausentes
   aparecem como `blocked` com a lista exata.
4. **Evidência**: a entrega exige plano, verificação e limitações; o recibo
   sempre tem `confidence_promoted=false` e `external_validation=false`.
5. **Orçamento**: passos e custo são limitados; esgotou, para.
6. **Sem cópia sem licença**: os adaptadores apontam para o diretório externo;
   não copiam conteúdo de terceiros para o repositório.
7. **Checagem segura**: `--safe-checks` executa apenas o `safe_argv` read-only
   declarado pelo adaptador; sem essa declaração, nada roda.

## Adaptadores conhecidos

- `archify` — diagramas HTML interativos; Apache-2.0; instalado.
- `image-story-video-wizard` — máquina de estados de 16 fases; MIT; instalado.
- `hbg-life-simulation` — pipeline HyperFrames/TTS/legendas/QA; MIT; pronto,
  com `hyperframes`, `media-use`, `code-video-visual-qa`, `imagegen` e
  CLIProxyAPI local autenticado.
- `code-video-visual-qa` — QA Core-native com ffprobe/ffmpeg; substitui a
  dependência homônima do hbg.
- `imagegen` — cliente OpenAI-compatible `generate`/`generate-batch`; usa
  apenas `OPENAI_API_KEY`/`OPENAI_BASE_URL` e exige loopback ou HTTPS.
- `opus-video-skills` — p5.js/three.js; MIT; requer Chrome.
- `reel-video` — CLI/review board; MIT; requer Grok/Codex.
- `distilly` — perfis de pessoa; MIT; exige consentimento e privacidade.
- `kdense-scientific-agent-skills` — catálogo de 177 SKILL.md; MIT; integrado.

## Limites

- A atenção executiva é uma heurística determinística e auditável; não é uma
  rede neural treinada e não certifica qualidade científica.
- `run` não renderiza vídeo, não executa OAuth, não abre navegador e não
  chama coletor. Ele prepara o plano e para no gate.
- Resultados de terceiros não são promovidos a confiança do Core.
