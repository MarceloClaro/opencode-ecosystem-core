---
name: imagegen
description: >
  Geração de imagens por endpoint OpenAI-compatible, com chave apenas no
  ambiente. Use para gerar uma imagem (`generate`) ou um lote JSONL
  (`generate-batch`) consumido pelo hbg-life-simulation, HyperFrames ou outro
  pipeline. Aceita o proxy local em loopback ou um endpoint HTTPS; não cria
  conta, não instala proxy e não promete entitlement. Sem OPENAI_API_KEY,
  devolve blocked.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R1069
spec: SPEC-935-R1069-centro-producao-global.md
---

# ImageGen — cliente OpenAI-compatible (R1069)

Implementação Core-native. Não é um gerador local: é o cliente que fala com o
backend escolhido pelo operador (CLIProxyAPI local, OpenAI Images ou outro
endpoint compatível).

## Configuração

```bash
export OPENAI_BASE_URL="http://127.0.0.1:8317/v1"
export OPENAI_API_KEY="<chave local do proxy ou do provedor>"
export HBG_IMAGE_MODEL="gpt-image-2"   # opcional
```

Regras:

- A chave vive somente no ambiente do processo; nunca é gravada no projeto,
  prompt, JSONL, log ou relatório.
- `http://` só é aceito em `127.0.0.1`, `localhost` ou `::1`; remoto exige
  `https://`.
- O endpoint precisa expor `POST /images/generations` e retornar
  `data[0].b64_json` ou `data[0].url`.

## Comandos

```bash
python3 skills/imagegen/scripts/image_gen.py generate \
  --model gpt-image-2 --prompt "sala vazia em estilo comic, sem texto" \
  --size 1536x1024 --out /tmp/imagegen-smoke.png --no-augment

python3 skills/imagegen/scripts/image_gen.py generate-batch \
  --input tmp/imagegen/prompts.jsonl --out-dir assets/generated \
  --concurrency 5 --no-augment
```

Formato do JSONL:

```json
{"id":"g01","prompt":"...","output":"sheets/g01.png","size":"1536x1024","model":"gpt-image-2"}
```

`output` é relativo ao `--out-dir`; caminhos absolutos e `..` são rejeitados.
Duplicatas de basename são rejeitadas para não sobrescrever imagens.

## Limites

- Consome quota/capacidade da conta quando o backend é autenticado.
- Não prova entitlement de imagem; um `/models` OK não garante geração.
- Não avalia qualidade estética, identidade de personagem ou adequação
  científica; a inspeção visual é humana.
- Não instala nem inicia proxy; isso é feito pelo operador/CLIProxyAPI.
- Nenhuma validação externa.
