---
spec_id: SPEC-935-R817
title: Instalação real e orientação reproduzível dos runtimes opcionais
component: integrations/runai.py
status: implemented
round_id: R817
test_file: tests/test_r817_runtime_installation.py
---

# SPEC-935-R817 — Runtimes opcionais disponíveis

## Problema

O diagnóstico registrou RunAI e Tig ausentes. O pacote npm indicado pelo
instalador RunAI respondeu HTTP 404. Recomendar o mesmo instalador na ausência
da CLI mantém uma orientação que não resolve essa pendência.

## Requisitos

1. A orientação de instalação do RunAI indica o repositório oficial, Bun,
   pnpm, compilação dos workspaces e RUNAI_SOURCE_DIR, sem executar um script
   remoto nem afirmar que o pacote npm está disponível.
2. Todas as superfícies de diagnóstico usam a mesma orientação. A resposta
   HTTP 404 continua sendo informada quando a sondagem é solicitada.
3. O diagnóstico estrutural continua sem rede. Uma instalação encontrada não
   dispara a consulta do pacote remoto. CLIs executáveis na .venv do projeto
   são localizadas também a partir do Python do sistema; overrides inválidos
   continuam explícitos e arquivos sem permissão não contam como instalação.
4. Instalações reais ficam isoladas fora do ambiente Python do Core. Os
   lançadores não sobrescrevem programas existentes e preservam argumentos.
5. Registros de versão, origem, ajuda real e diagnóstico distinguem instalação,
   prontidão do backend e inferência. Ausência de modelo ou credencial não é
   convertida em inferência realizada.
6. A saúde HTTP exige identidade `service=runai`, `ok=true` e PID inteiro
   positivo. Um serviço diferente ou resposta malformada não confirma prontidão.
   `stop` conserva a saída da CLI e não declara sucesso se o servidor
   identificado continuar respondendo, mesmo com código de saída zero.
   Timeouts, erros HTTP e identidade inválida preservam estado desconhecido;
   somente conexão recusada confirma ausência. Nenhum erro de transporte é
   promovido a término confirmado.

## Aceite

Contraprovas herméticas para as orientações e a ausência de consultas remotas;
execução real das CLIs instaladas; diagnóstico do Core após instalação; logs e
manifesto de procedência em outputs/core-r817. A instalação não configura
provedores comerciais nem concede validação científica externa.

## Execução local

- Orientações: RED 3 falhas/1 aprovação; resolução .venv RED 1 falha/5
  aprovações; identidade/stop RED 9 falhas/8 aprovações.
- RunAI 0.2.1 compilado, CLI real, bindings e três modelos locais identificados.
  Duas provas HTTP reais passaram, e a entrada central concluiu chat,
  completion, embedding e ciclo de início/término do daemon.
- Tig 0.1.7 instalado em ambiente Python 3.12.14 isolado; ajuda real passou.
- Diagnóstico estrutural e live posteriores: 21 pass, 0 warn, 0 fail.
  O diagnóstico upstream do RunAI conserva os avisos de equipamento sem GPU.
- logs completos em outputs/core-r817, limites em docs/RUNTIMES_OPCIONAIS.md.
