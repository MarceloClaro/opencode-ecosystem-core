# HuggingFace Hub — Configuração do Profile (Passos Manuais)

## Status Atual

| Item | Status | Método |
|---|---|---|
| Repositório criado | ✅ | API |
| 976 arquivos uploadados | ✅ | CLI |
| Dataset card (README) | ✅ | Arquivo |
| .gitattributes (LFS) | ✅ | Arquivo |
| Repo público | ✅ | API |
| Repo non-gated | ✅ | API |
| **Bio do profile** | ⏳ | **Web UI** |
| **Links do profile** | ⏳ | **Web UI** |
| **Foto do profile** | ⏳ | **Web UI** |
| **Collection** | ⏳ | **Web UI** |

## Passo 1: Atualizar Bio do Profile

1. Acesse: https://huggingface.co/settings/profile
2. No campo **"Full name"**, mantenha: `Marcelo Claro`
3. No campo **"Bio"**, adicione:

```
OpenCode Ecosystem Core Developer | Multi-Agent Orchestration | Scientific Research Automation | 205 Agents, 303 Specs, 160 Research Proposals | Qualis A1 Auto-Score 97/100
```

4. Clique em **"Save"**

## Passo 2: Adicionar Links

1. Na mesma página de profile
2. Seção **"Links"** ou **"Social"**
3. Adicione:

| Tipo | URL |
|---|---|
| GitHub | `https://github.com/MarceloClaro` |
| Website | `https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core` |
| Twitter/X | (se disponível) |

4. Clique em **"Save"**

## Passo 3: Foto do Profile

1. Na página de profile, clique no **ícone de avatar**
2. Faça upload de uma foto profissional
3. Recomendação: foto com fundo neutro, olhando para câmera

## Passo 4: Criar Collection

1. Acesse: https://huggingface.co/collections
2. Clique em **"New collection"**
3. Preencha:

| Campo | Valor |
|---|---|
| **Name** | `OpenCode Ecosystem` |
| **Description** | `Ecossistema completo de orquestração multi-agente, pesquisa científica e automação - 205 agentes, 303 specs, 160 propostas de pesquisa` |
| **Visibility** | Public |

4. Adicione os seguintes repositórios à collection:

| Repositório | Tipo |
|---|---|
| `marceloclaro/opencode-ecosystem-core` | Dataset |
| `marceloclaro/opencode-research` | Dataset |

5. Clique em **"Create"**

## Passo 5: Verificar Repositórios

Após configurar, verifique:

1. https://huggingface.co/marceloclaro — Profile page
2. https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core — Main repo
3. https://huggingface.co/datasets/marceloclaro/opencode-research — Research repo
4. https://huggingface.co/collections — Collection page

## URLs Importantes

| Recurso | URL |
|---|---|
| Profile | https://huggingface.co/marceloclaro |
| Settings | https://huggingface.co/settings/profile |
| Core Repo | https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core |
| Research Repo | https://huggingface.co/datasets/marceloclaro/opencode-research |
| Collections | https://huggingface.co/collections |
| API Token | `hf_***REDACTED***` |

## Notas

- O profile já tem avatar (produção HF)
- Repos são públicos e non-gated
- Dataset card está completo com YAML metadata
- .gitattributes configurado para LFS automático
- 976 arquivos uploadados com sucesso
