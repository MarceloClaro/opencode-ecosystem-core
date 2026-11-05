# SPEC-935-R1064 — OpenMontage externo, LiteLLM e auditoria de extensões

**Status:** OpenMontage instalado e testado; LiteLLM configurado e com Gemini
funcional; Groq/Cerebras/OpenRouter aguardam chaves. Extensões do Antigravity e
plugins do Codex foram auditados, não copiados.

## 1. OpenMontage

- Projeto externo em `external/OpenMontage` (fora do Git), licença **AGPL-3.0**.
- Instalação com `make setup` concluída; `pytest` de contratos: **1270 passed,
  7 skipped**.
- Runtime de composição: FFmpeg, Remotion e HyperFrames reportados como
  disponíveis no preflight; o doctor do HyperFrames expirou no setup e deve ser
  revalidado antes de confiar nele.
- Demo zero-key `code-to-screen` renderizado: 1920×1080, 30 fps, 25,045 s,
  3.697.814 bytes, SHA-256
  `8177d9b21e63581d2361a0eb4aa3f9f38493818dd63a1ff7c676e4f073aae4f9`.
- **Não incorporar código AGPL ao Core** sem parecer jurídico; usar como
  ambiente externo, com projeto e venv próprios.

## 2. LiteLLM

- `litellm[proxy]` **1.108.0** em
  `~/.cache/opencode-pilot/venvs/litellm` (Python 3.12).
- Config: `config/litellm.yaml`; launcher: `scripts/litellm_start.sh`.
- Quatro grupos: `free-gemini`, `free-groq`, `free-cerebras`,
  `free-openrouter`, com fallback circular entre eles.
- Proxy validado em `127.0.0.1:4018`: `/health/liveliness` 200 e `/v1/models`
  listou os quatro grupos.
- Chamada real via proxy: `free-gemini` com `gemini-3.5-flash-lite` retornou
  **“OK”**. `gemini-2.5-flash` e `gemini-3.8-flash` falharam por
  descontinuação/503; o modelo foi corrigido para 3.5 Flash Lite.
- Groq, Cerebras e OpenRouter estão **sem chave** neste host; o fallback tenta
  e falha com `Invalid API Key`. Não há como inventar acesso gratuito sem
  credencial e respeito aos termos.
- `.env.litellm` tem modo `0600`, está no `.gitignore` e não é versionado.

## 3. Fallback e limites

- Fallback só deve ocorrer em 429/quota/5xx/timeout; não em recusa de conteúdo.
- Para pesquisa de alto risco, registrar qual modelo respondeu; não trocar
  silenciosamente por um modelo mais fraco.
- Free tiers mudam; verificar termos e cotas antes de automatizar.
- Não usar contas compartilhadas, scrapers ou APIs reversas para “Claude/GPT
  ilimitado”.

## 4. Antigravity IDE — `C:\Users\marce\.antigravity-ide\extensions`

- 32 extensões; maioria é tooling de IDE (Python, Jupyter, PowerShell, SQLite,
  PDF/DOCX/LibreOffice, GitLens, Go, C/C++, Ruby, visualizadores científicos).
- Apenas duas expõem MCP: **Image Studio** (MIT; crop/resize/compress) e
  **Google Cloud Data Agent Kit** (licença própria; GCP). Nenhuma adiciona
  busca literária, citação, agente de vídeo ou orquestração que o Core já não
  tenha.
- **Decisão:** não integrar as extensões ao Core. Elas são úteis apenas dentro
  do Antigravity IDE; o Core usa FFmpeg/Pillow/Remotion e Python científico.

## 5. Codex — `C:\Users\marce\.codex`

- 2,3 GB; configuração, sessões, plugins e marketplaces.
- Plugins habilitados incluem documentos/PDF/planilhas/apresentações da OpenAI,
  browser/computer-use, Claude Cowork (bio-research, data, design, engenharia,
  finance, legal etc.) e os plugins do próprio Core (`opencode-ecosystem-core`,
  `opencode-rea`, `opencode-lean4`, `opencode-mirofish-offline`).
- A maior parte é **proprietária ou dependente de conta/assinatura**; não copiar
  código, prompts ou credenciais.
- **Decisão:** usar o Codex como executor externo para tarefas que dependem
  desses plugins (documentos, PDF, planilhas, apresentações, Consensus/NGS) e
  não como dependência do Core. Registrar plugin, conta, custo e limites.

## 6. Segurança

- A execução de depuração do launcher LiteLLM imprimiu a chave Gemini no log
  local. **Recomenda-se revogar/rotacionar a chave** no Google AI Studio antes
  de compartilhar logs ou sessão.
- Nenhuma chave foi versionada; `.env.litellm` é ignorado.
- OpenMontage e plugins externos não foram executados com credenciais do
  usuário além do teste Gemini.
- Nada foi publicado; não há validação externa.

## 7. Próximos passos

1. Repor as chaves Groq/Cerebras/OpenRouter e testar o fallback real por 429.
2. Revalidar HyperFrames (`make hyperframes-doctor`) antes de usá-lo.
3. Avaliar `ffmpeg-skill` (MIT, 42 ferramentas, MCP) como próxima integração de
   vídeo; `blender-skills` e `manim-skill` exigem Blender/Manim instalados.
4. Integrar LiteLLM ao OpenCode como provider opcional
   (`http://127.0.0.1:4000/v1`), sem torná-lo padrão.
