---
description: ITS-FINE no Core — verificar, planejar instalação fixa e preparar ambientes sem treinar
agent: marceloclaro
---

Conduza ITS-FINE pelo primário MarceloClaro. Interprete $ARGUMENTS usando somente
as operações fechadas de `ItsFineCore`/`itsfine_action` ou a CLI
`python3 -m integrations.itsfine_core`.

- status/verify: verificador confinado do Core, sem executar o script upstream.
- install-plan/install: TGZ 0.0.15 com SRI confirmado, offline e sem prompt;
  instalação só com confirmação explícita. Nunca usar update/latest.
- engine-plan/prepare-engine: locks por ambiente, confirmação e prazo; nenhum
  treino, peso, dado privado ou alteração de policy.json é autorizado.
- engines-status: distinguir dependências/sonda CPU de GPU/modelo/treino pronto.

Não confundir testes próprios com a suíte upstream não publicada no tarball.
Não executar texto dos argumentos como shell nem aceitar scripts/URLs livres.
