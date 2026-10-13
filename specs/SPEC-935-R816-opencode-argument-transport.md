---
spec_id: SPEC-935-R816
title: Comandos OpenCode com transporte JSON sem interpolação de código
component: integrations/opencode_cli.py, integrations/opencode_commands.py, .opencode/tools/core_command.ts
status: green
round_id: R816
test_file: tests/test_r816_opencode_argument_transport.py
---

# SPEC-935-R816 — Argumentos como dados

## Problema

Templates legados inseriam `$ARGUMENTS` dentro de código Python e comandos
shell. Uma consulta com apóstrofo interrompia `/reason`; aspas, caminhos e
metacaracteres também alteravam a linguagem executada. A documentação oficial
define `template` como prompt, e não como uma API de argumentos de processo.

## Requisitos

1. Preservar todos os nomes e capacidades dos comandos. Prompts legados usam
   `agent=marceloclaro` e a ferramenta local `core_command`.
2. A ferramenta é desabilitada globalmente e habilitada apenas no primário,
   impedindo que perfis com `bash=deny` contornem sua permissão.
3. A ferramenta envia JSON no stdin a um módulo Python fixo, sem shell.
   Comandos são uma lista explícita; argumentos textuais e argv em lista não
   são código, nomes de módulos ou instruções de shell.
4. Reason, diagnose e MASWOS mantêm operações centrais existentes; diagnose
   executa a camada profunda por padrão (IVA, SNS, SCE e sucessores), inclusive
   quando invocado pela configuração salva ou recém-gerada. Route,
   PyPI e TDD mantêm seus motores reais. Falhas retornam erro e código não zero.
5. TDD valida alvo local e opções antes de iniciar pytest. CLIs auxiliares
   recebem somente argv explícito, preservando opções administrativas autorizadas.
6. Processos têm prazo finito, cancelamento, coleta de resultados e limpeza.
7. Testes reproduzem RED com apóstrofo e GREEN com aspas, Unicode, caminhos com
   espaços e metacaracteres, sem executar marcadores incluídos na entrada.

## Fronteira upstream

O OpenCode 1.18.4 expande a sintaxe especial inline de shell depois de substituir
argumentos e antes de `command.execute.before`. Esta correção elimina a
interpolação de código dos templates e protege a entrada JSON da ferramenta;
não modifica nem promete blindagem do parser textual upstream. Não se deve
confundir uma chamada estruturada de `core_command` com essa sintaxe externa.

Referências primárias:
- https://opencode.ai/docs/commands/
- https://opencode.ai/docs/custom-tools/
- https://github.com/anomalyco/opencode/blob/v1.18.4/packages/opencode/src/session/prompt.ts

## Evidência

RED, GREEN, prova do transporte e hashes ficam em `outputs/core-r816`.
Resultados são operações locais; não atestam inferência LLM, autoria de
manuscrito, validação externa ou classificação editorial Qualis.

- RED: `/reason` legado com apóstrofo retornou 1 e `SyntaxError`; os 17
  contratos iniciais falharam antes da implementação. Uma regressão adicional
  demonstrou que um envelope incompleto com `success=true` precisava ser
  rejeitado mesmo com código de saída zero.
- GREEN: 57 testes R394/R816 passaram em 208,08 s. Depois da última mudança
  de limpeza, os nove testes reais da ferramenta passaram em 16,87 s; a união
  dos relatórios cobre 58 casos distintos, incluindo o novo caso de descendente
  sobrevivente ao encerramento do helper.
- Os 21 nomes legados executaram suas operações reais pelo helper; CLIs sem
  entrada provaram seus contratos de ajuda/disponibilidade. `claude-sdk options`
  preservou argv com apóstrofos e metacaracteres sem realizar inferência.
- Dois mutantes da fonte final, em cópias isoladas, foram mortos: desabilitar
  a guarda do agente primário e aceitar envelope incompatível.
- A configuração foi regenerada e reproduzida com 254 agentes, 16 MCP e 30
  comandos. O typecheck isolado da ferramenta passou; o ajuste ESM global
  pertence à revisão R819.

## Continuidade do contrato profundo (R496, 2026-10-11)

O gate amplo encontrou duas regressões que ainda procuravam `deep=True`
dentro dos antigos templates Python. O dispatcher já preservava esse padrão;
a falha estava na representação esperada pelos testes. As duas provas agora
executam a ferramenta TypeScript real, o transporte JSON e o orquestrador
central, tanto pela configuração salva quanto pela configuração gerada.
Exigem IVA, SNS, SCE e sucessores no diagnóstico de um documento do repositório.

- RED anterior preservado: duas falhas e um passe no contrato R496.
- Gate final R496/R816/R394: 71 testes passaram em 282,16 s, sem falhas,
  erros ou skips. Nenhuma mudança operacional foi necessária nesta etapa.
- Dois mutantes isolados foram mortos: remover a camada profunda do
  dispatcher e desviar a rota configurada de diagnose para reason. No primeiro,
  a ferramenta executou e o resultado perdeu `inertia`, causando a falha esperada.
- Um gate concorrente anterior atingiu o limite original de 90 s na primeira
  chamada enquanto ocorria renderização pesada; os demais 70 casos passaram.
  O mesmo teste passou frio em 28,28 s. Esse relatório foi preservado e o gate
  completo foi repetido sem elevar prazos ou enfraquecer assertivas.

Evidências: `outputs/core-r816/regression-{r496-red,green,concurrent-timeout,
route-cold,mutation,summary}`. A prova cobre a entrada estruturada local;
não demonstra a interpretação do prompt por um modelo nem altera a fronteira
upstream já descrita acima.
