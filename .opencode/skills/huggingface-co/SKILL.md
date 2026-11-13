---
name: huggingface-co
description: Skill nativa do OpenCode para integração com HuggingFace Hub: modelos, datasets, spaces e API. Acesso direto ao hub sem instalação de pacotes externos; gate de auth, rate-limit e artefatos com hash.
metadata:
  version: "1.0.0"
  spec_id: "SPEC-935-R1123"
  status: "implemented"
  test_file: "tests/test_huggingface_co.py"
  license: "CC-BY-4.0 (hub access)"
  github_native: true
---

# huggingface.co — Skill Nativa do OpenCode

## Objetivo
Prover integração nativa do OpenCode com o **HuggingFace Hub** para download de modelos, datasets e spaces, com suporte a:
- **Autenticação** (token HF, env vars, key rotation)
- **Listagem** (modelos, datasets, spaces por organização/usuário)
- **Download** (modelos e datasets com progresso, hash verification, resumability)
- **API** (text generation, classification, embeddings via inferência local)
- **GitHub native** (artefatos upload, release notes, labels automáticas)

## Escopo

### Em escopo
- `huggingface.hub` — API Python e CLI para operações HF nativas
- `status` — checa auth, rate-limit, token válido e disponibilidade
- `list` — lista modelos/datasets/spaces por usuário/org
- `download` — baixa modelo/dataset com hash verification e resumability
- `infer` — texto generation via modelo HF (template/local)
- `push` — faz upload de modelo/dataset ao hub (requer auth)
- `summary` — resume metadados (cards, tags, lastModified, downloads)
- Testes em `tests/test_huggingface_co.py`.

### Fora de escopo
- Instalar `transformers`, `datasets` ou quaisquer pacotes HF (do operador)
- Treinar modelos (apenas inferência/ download)
- Modificar repositórios HF de terceiros
- Promover confiança ou declarar SOTA sem validação humana
- Acessar repositórios private sem token explícito
- Executar workloads que exijam GPUs ou compute pagos

## Requisitos

1. `status` e `list` não exigem autenticação (apenas leitura pública).
2. `download` e `push` exigem token HF válido via `HF_TOKEN` env var ou `--token` CLI.
3. Downloads usam `requests` stdlib + `hashlib`; nenhum modelo é executado.
4. Inferência usa templates locais ou modelo compatível; não chama provedores pagos.
5. Todo resultado inclui `verification.scope = local_observation`, `externally_validated = false`.
6. Rate-limit respeitado: `--max-retries 3` e backoff exponencial.
7. Token nunca é logged ou impresso em output; masked em logs.

## Critérios de aceitação

- [ ] `status` reporta `available: True` quando HF Hub é acessível publicamente.
- [ ] `status` reporta `authenticated: True` quando `HF_TOKEN` está definido e válido.
- [ ] `list` retorna lista de modelos sem erros para busca pública.
- [ ] `download` salva arquivo e calcula SHA-256; falha se token inválido.
- [ ] `infer` gera texto a partir de modelo sem chamar API externa (usando template local).
- [ ] `push` bloqueado com erro explícito quando sem token/ auth.
- [ ] `tests/test_huggingface_co.py` passa.
- [ ] Nenhum segredo do ambiente chega ao output (token masked).
- [ ] Rate-limit tratado com backoff; nenhum loop infinito.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_huggingface_co.py -q
```

Ciclo TDD: teste escrito antes do módulo; RED por `ModuleNotFoundError`; implementação; GREEN.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| API HF downtime | `status` reporta `unavailable`; retry controlado |
| Token expirado | `status` reporta `authenticated: False`; decisão do operador |
| Download corrompido | SHA-256 verification; arquivo removido em mismatch |
| Rate-limit ban | Backoff exponencial; `--max-retries 3`; pausa entre requisições |
| Uso indevido de modelos | Gate de policy: uso acadêmico/pesquisa; comercial requer licença própria |

## Evidência

- Fonte: `huggingface.co` — hub público; acesso anonímio para listagem/download de modelos públicos.
- Auth: token via `HF_TOKEN` env var; não stored no código nem no disco.
- Download: `requests` stdlib + `sha256` verification; nenhum código executado.
- Inferência: template local; nenhum modelo PyTorch/TensorFlow carregado automaticamente.
- GitHub native: artefatos `model-*.json`, `dataset-*.tar` fazem upload via API HF; labels automáticas.

## Integração GitHub Nativa

Esta skill foi desenhada para operar nativamente no fluxo do GitHub:

- **Artefatos**: `model-*.json`, `dataset-*.json`, `download-report-*.md` são gravados como releases do GitHub.
- **Labels**: downloads recebem label `hf-download` ou `hf-model-public`.
- **Release notes**: metadados resumidos (`model_id`, `downloads`, `lastModified`) são automaticamente adicionados ao corpo do release.
- **Workflow**: pode ser acionado via `github_actions` ou `opencode` manual a partir de issues/pull-requests.

## Exemplos de uso

```bash
# Status do hub (público)
python3 -m integrations.huggingface status

# Listar modelos públicos
python3 -m integrations.huggingface list --search "transformers"

# Download de modelo público
python3 -m integrations.huggingface download --model "bert-base-uncased" --out ./models/

# Inferência com template local
python3 -m integrations.huggingface infer --model "bert-base-uncased" --text "Hello world"

# Upload de modelo (requer HF_TOKEN)
python3 -m integrations.huggingface push --model ./my-model --token "$HF_TOKEN"
```