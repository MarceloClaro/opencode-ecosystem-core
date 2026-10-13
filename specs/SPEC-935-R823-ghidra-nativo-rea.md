---
spec_id: SPEC-935-R823
title: Análise binária estática Ghidra sob REA e MarceloClaro
component: integrations/rea_bridge, marceloclaro/rea_cli, marceloclaro/rea_reports
status: implemented
round_id: R823
test_file: tests/test_r823_ghidra_native_rea.py
---

# SPEC-935-R823 — Provider nativo Ghidra

## Objetivo e arquitetura

Completar a análise nativa gratuita do REA 6.4.0 com Ghidra 12.1.4 oficial e
JDK completo isolados fora do Core. MarceloClaroOrchestrator.rea_action continua
como entrada. A análise JavaScript `analyze` mantém seu contrato existente.

## Contratos de aceite

1. `analyze_binary` recebe arquivo local explícito, até 128 MiB, `procedure`
   textual (padrão `main`, até 256 caracteres), e prazo finito até 180 segundos.
   Diretórios, NUL, campos/operações desconhecidos são rejeitados antes do MCP.
2. Uma sessão MCP isolada executa somente `open_binary` com provider_id=ghidra,
   `analyze_function`, `binary_session` e `close_binary`. Não executa o alvo,
   depura, altera metadados, instala componentes nem invoca operações arbitrárias.
3. GHIDRA_INSTALL_DIR e JAVA_HOME explícitos têm precedência; valores inválidos
   não recorrem à instalação padrão. Ausência permite os caminhos isolados
   declarados em ~/.local/share/opencode-core/native-rea. Não muda os defaults
   de Java do sistema. Disponibilidade estática não comprova sessão real.
4. A conclusão exige Evidence da função, provider Ghidra/version, digest do alvo
   compatível, sessão aberta correspondente e fechamento confirmado. Erro,
   resultado parcial/incompatível, mutação do alvo e falha de fechamento não
   viram sucesso. Respostas integrais e hash permanecem preservados.
5. Timeout/cancelamento cancelam a operação e fazem fechamento blindado e limitado
   antes da limpeza do processo MCP. A integração cooperativa usa R825.
6. CLI e MCP preservam coordenação, resumos finitos e artefatos integrais. Testes
   herméticos RED/GREEN são separados de compilação e análise real de fixture C
   próprio, nunca executado. Proveniência oficial, hashes, provider/version,
   sessão, limpeza e limitações são registradas em outputs/core-r823.

## Fontes e limites

Ghidra: https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build
(Apache-2.0). JDK: https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1
(GPL-2.0 com Classpath exception). REA: https://github.com/MarceloClaro/rea.
Pseudocódigo é resultado de análise estática; não equivale ao código-fonte original
nem comprova comportamento dinâmico ou validação externa. Esta extensão não
transforma o catálogo inteiro do REA em capacidades delegáveis do Core.

## Evidência executada

Instalação isolada com hashes oficiais: Ghidra 12.1.4 e Temurin JDK 21.0.12.1+1.
O Java global 25 permaneceu inalterado. REA 6.4.0 confirmou provider Ghidra
disponível e 170 ferramentas pelo launcher MCP real do Core. O doctor explícito
de Ghidra passou; as advertências de clientes opcionais/Hopper continuam separadas.

O gateway primário analisou ELF próprio sem permissão de execução e recuperou
`fixture_add`, cujo pseudocódigo soma os argumentos e 7; digest original
preservado e marker de execução ausente. `close_binary` retorna `result=null`;
um `binary_session` posterior comprovou `open=false`. Evidência completa por
hash, com versão do provider, perfil e linhagem de processos, foi exportada.

Cancelamento real durante importação encerrou Node/Java e removeu o projeto
temporário antes de retornar. Timeout real de 10 segundos retornou falha e
também encerrou os processos/removeu o projeto; neste caso a confirmação MCP
de fechamento não chegou, e a ponte manteve `cleanup.closed=false`.

RED inicial: 14 falhas; RED launcher/status: 2; RED contrato de fechamento: 2;
RED cancelamento anterior à criação do transporte: 1.
GREEN focado: 87 casos R808/R823. Regressão ampla final: 134 casos incluindo integração,
superfície de rede e cancelamento R825. Provas reais, relatórios, comandos,
hashes e limitações permanecem separados em `outputs/core-r823`.
Três mutantes de provider, digest e confiança em ACK de fechamento foram mortos
por regressões específicas em cópias isoladas da fonte, sem editar o produto.
