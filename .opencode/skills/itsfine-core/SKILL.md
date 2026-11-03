---
name: itsfine-core
description: Integra ITS-FINE ao primário MarceloClaro para status, integridade, planejamento e diagnóstico retomável. Use para itsfine no Core; treino e permissões exigem decisão humana.
---

# ITS-FINE sob o Core

## Atualização R924–R926

Entrada canônica: `python3 -m marceloclaro.cli itsfine` ou `/itsfine` após
reiniciar o OpenCode. `verify` usa o verificador confinado Core. Há
install-plan/install e engine-plan/prepare-engine, sempre com plano fechado,
SRI/locks e confirmação para efeitos. Nunca usar update/latest por automação.
`engines-status` diferencia dependências/sonda CPU de GPU/treino pronto.
Consultar `docs/ITSFINE_CORRECOES_R924.md`. Testes do autor ausentes no tarball
continuam declarados ausentes; testes próprios não são a suíte upstream.

MarceloClaro continua sendo o primário. Use `ItsFineCore` por composição, não
altere arquivos do instalador nem `.its-fine/policy.json`. Origem auditada 0.0.15;
instalação e hashes não provam treino, qualidade ou prontidão dos motores.

1. Consulte memória e `python3 -m integrations.itsfine_core status`.
2. Planeje com `python3 -m integrations.itsfine_core plan [--run-id ID]`.
3. Para executar somente os diagnósticos fixos, use `run [--run-id ID]` ou
   `MarceloClaroOrchestrator.itsfine_action({'operation':'run','plan':plano})`.
4. Resultado `awaiting_human` não é rodada treinada nem skill executada.
5. Para continuar uma etapa de dados/treino, leia o SKILL.md correspondente em
   `.agents/skills/fine-*/`, respeite sua política de invocação e os contratos
   do projeto. Nunca acione implicitamente skills-filhas desabilitadas.
6. Não conceda allow_process, dados, transferência, Colab/Kaggle ou acesso a
   credenciais. Ausência de dados/autorizações resulta em plano e pendências.

REA já inspecionou o pacote distribuído em modo estático. Sua cobertura JS
não certifica o runtime Python. Consulte `docs/ITSFINE_CORE_R923.md` para os
gaps observados, recibos de instalação e fronteiras desta adaptação original.
