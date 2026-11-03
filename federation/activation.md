# MCPs federados ativados — R1015

Gerado em `2026-11-02T00:26:24Z`. Fonte: `federation/activated.json`.

> Ativação exige instalação íntegra, probe e smoke com vínculo idêntico e idade até 24 h.
> Instalação e recibo não provam disponibilidade futura. Opcionais instalados: `mcp-everything`, `executeautomation-playwright`; reativação via `--ids` somente com probe e smoke realmente válidos.

| Servidor | Pacote | Versão | Licença | Ferramentas | Probe | Smoke |
|---|---|---|---|---:|---|---|
| `chroma` | `chroma-mcp` | 0.2.6 | Apache-2.0 | 13 | válido | válido |
| `context7` | `@upstash/context7-mcp` | 4.4.4 | MIT | 2 | válido | válido |
| `mcp-memory` | `@modelcontextprotocol/server-memory` | 2.0.1 | MIT | 9 | válido | válido |
| `mcp-time` | `mcp-server-time` | 2026.10.28 | MIT | 2 | válido | válido |
| `playwright` | `@playwright/mcp` | 0.0.84 | Apache-2.0 | 25 | válido | válido |
| `qdrant` | `mcp-server-qdrant` | 0.8.1 | Apache-2.0 | 2 | válido | válido |

## Limites declarados

- **chroma**: Cliente persistente local; dados ficam em .opencode/mcp/federated/data/chroma.
- **context7**: Sem CONTEXT7_API_KEY a cota anônima é limitada; a chave é do operador.
- **mcp-memory**: Grafo de conhecimento em memória do processo; persistência exige MEMORY_FILE_PATH.
- **playwright**: Navegador headless com perfil isolado em memória (--isolated); este pacote exige Chrome for Testing compatível; instalar explicitamente com 'playwright-mcp install-browser chrome-for-testing'.
- **qdrant**: Servidor Qdrant local em 127.0.0.1:6333, container rootless `qdrant-core`; requer o container ativo. A primeira inicialização baixa o modelo FastEmbed do Hugging Face; o handshake não prova geração de embeddings.

## Comandos

```bash
python3 -m marceloclaro.cli federacao probe
python3 -m marceloclaro.cli federacao activate
python3 -m marceloclaro.cli federacao smoke
python3 -m marceloclaro.cli federacao doctor
```
