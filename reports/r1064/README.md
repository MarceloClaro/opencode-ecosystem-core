# R1064 — OpenMontage, LiteLLM e auditoria de extensões

**Status:** OpenMontage instalado e testado; LiteLLM operacional com Gemini;
fallback completo aguarda chaves. Extensões do Antigravity e do Codex não foram
copiadas. Nada publicado; sem validação externa.

## 1. OpenMontage (externo, AGPL-3.0)

| Item | Resultado |
|---|---|
| Caminho | `external/OpenMontage` (ignorado pelo Git) |
| Setup | `make setup` concluído |
| Contratos | **1270 passed, 7 skipped** |
| Demo zero-key | `code-to-screen`: 1920×1080, 30 fps, 25,045 s, 3.697.814 bytes |
| SHA-256 | `8177d9b21e63581d2361a0eb4aa3f9f38493818dd63a1ff7c676e4f073aae4f9` |
| Runtimes | FFmpeg/Remotion/HyperFrames no preflight; doctor do HyperFrames expirou no setup |

**Decisão:** manter como ambiente externo. AGPL não deve ser incorporada ao Core
sem revisão jurídica.

## 2. LiteLLM (MIT no núcleo)

| Item | Resultado |
|---|---|
| Versão | 1.108.0 |
| Venv | `~/.cache/opencode-pilot/venvs/litellm` (Python 3.12) |
| Config | `config/litellm.yaml` |
| Launcher | `scripts/litellm_start.sh` |
| Health/models | 200; quatro grupos listados |
| Teste real | `free-gemini` → `gemini-3.5-flash-lite` → **OK** |
| Groq/Cerebras/OpenRouter | sem chave; fallback falha com `Invalid API Key` |

O fallback circular está configurado, mas **não foi validado com as quatro
chaves**. Não há “free ilimitado”: free tiers mudam e exigem credencial.

## 3. Antigravity extensions

`C:\Users\marce\.antigravity-ide\extensions` — 32 extensões.

| Grupo | Extensões | Uso para o Core |
|---|---|---|
| Python/Jupyter | Python, Debugger, Pyrefly, Jupyter | pesquisa interativa; Core já tem Python |
| Documentos | PDF, DOCX/ODT, LibreOffice preview, Markdown PDF, Markdown Them | inspeção GUI; Core usa pdftotext/pandoc/python-docx |
| Dados | SQLite, SQLTools, Scientific Data Viewer, Scientific Image Visualizer | GUI para HDF5/NetCDF/Zarr/GeoTIFF; Core pode usar xarray/h5py/rasterio |
| Imagem | Image Studio (MCP), SVG manager, Miconvert | Image Studio tem MCP MIT, mas duplica Pillow/FFmpeg |
| Infra | GitLens, GitHub Actions, Go, clangd, Ruby LSP, PowerShell, GCP Data Agent Kit | tooling de IDE; nada ausente no Core |

**Decisão:** não integrar. Apenas Image Studio e GCP Data Agent Kit expõem MCP;
o primeiro duplica processamento de imagem, o segundo exige GCP. Os viewers
científicos são úteis dentro do IDE, não como backend.

## 4. Codex home

`C:\Users\marce\.codex` — 2,3 GB.

- Plugins habilitados: documentos/PDF/planilhas/apresentações (OpenAI),
  browser/computer-use, Claude Cowork (bio-research, data, design, engineering,
  finance, legal, marketing, productivity) e os plugins do Core.
- Marketplaces locais/remotos incluem Consensus, Google Drive, Gmail, Canva,
  NGS analysis, sequence viewer, creative-production etc.
- A maior parte é proprietária ou dependente de conta/assinatura.
- **Decisão:** usar Codex como executor externo para tarefas que precisem
  desses plugins; não copiar código, prompts ou credenciais para o Core.

## 5. Segurança

- O debug do launcher LiteLLM imprimiu a chave Gemini no log local. **Rotacionar
  a chave** no Google AI Studio antes de compartilhar logs.
- `.env.litellm` está em modo 0600 e no `.gitignore`.
- Nenhum plugin de terceiro foi executado com credenciais do usuário.
- Nada foi publicado.

## 6. Próximo passo recomendado

1. Repor chaves Groq/Cerebras/OpenRouter e testar 429 real.
2. Revalidar HyperFrames.
3. Avaliar `ffmpeg-skill` (MIT, 42 ferramentas, MCP) como integração de vídeo.
4. Só depois avaliar `blender-skills` e `manim-skill` (exigem Blender/Manim).
