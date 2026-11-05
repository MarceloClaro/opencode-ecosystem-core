---
name: imagegen
description: >
  Cliente Core-native de geração de imagens OpenAI-compatible. Use para
  `generate` ou `generate-batch` contra CLIProxyAPI local ou endpoint HTTPS,
  inclusive no pipeline hbg-life-simulation. A chave vem só do ambiente; sem
  OPENAI_API_KEY o resultado é blocked. Não instala proxy, não cria conta e não
  garante entitlement de imagem.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R1069
spec: SPEC-935-R1069-centro-producao-global.md
---

# ImageGen (Core-native)

Implementação canônica em `skills/imagegen/`:

```bash
python3 skills/imagegen/scripts/image_gen.py generate \
  --model gpt-image-2 --prompt "..." --size 1536x1024 --out /tmp/img.png --no-augment

python3 skills/imagegen/scripts/image_gen.py generate-batch \
  --input prompts.jsonl --out-dir assets/generated --concurrency 5 --no-augment
```

O caminho `~/.codex/skills/.system/imagegen` é um link para esta implementação,
para compatibilidade com o hbg. Credenciais apenas em `OPENAI_API_KEY` e
`OPENAI_BASE_URL`; loopback ou HTTPS. Não há validação externa.
