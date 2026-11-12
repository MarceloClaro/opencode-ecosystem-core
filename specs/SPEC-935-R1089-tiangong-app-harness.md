# SPEC-935-R1089 — Técnicas Tiangong e harness original local

## Demanda e autoridade
Investigar, com REA sob MarceloClaro, exclusivamente as aplicações públicas
`https://tiangongqs.com/application/quantum-application/{HDR,RSIR,VRP}` e transformar
técnicas observáveis em agentes reutilizáveis, harness, skill e MCP local.
Não copiar implementação/identidade proprietária, não autenticar, não submeter
jobs remotos, não instalar dependências nem habilitar MCP externo.

## Plano (antes da implementação)
1. Coletar HTML e bundles públicos referenciados, com URL, data UTC e SHA-256.
2. Analisar estaticamente os artefatos com REA; conferir UI se runtime disponível.
3. Publicar matriz observado/inferido/desconhecido e desenho original delimitado.
4. Escrever testes negativos/positivos, observar RED e implementar adaptação local.
5. Reutilizar especialistas existentes; perfis novos somente via lifecycle do primário.
6. Publicar skill, contratos MCP desativados e documentação de execução.
7. Executar regressões, revisão independente, reflexão e registro evolutivo.

## Critérios de aceitação
- AC1: três alvos identificados por evidências rastreáveis; ausências explícitas.
- AC2: pelo menos uma análise real REA do artefato público, com recibo e hash.
- AC3: não alegar acesso ao backend, treinamento, execução quântica, vantagem
  quântica ou reprodução equivalente sem evidência.
- AC4: harness original limitado, entradas e saídas JSON documentadas, resultados
  determinísticos e validação estrita de números/dimensões/orçamentos.
- AC5: testes unitários e transporte MCP real local; negativos para entrada inválida,
  operação desconhecida e demanda de provedor indisponível. Sem rede na execução local.
- AC6: skill invocável e roteamento por agentes subordinados a MarceloClaro; não
  confundir perfil registrado com inferência executada.
- AC7: alterações pré-existentes não sobrescritas. MCP preparado e desativado por
  padrão; não trocar configuração compartilhada inteira.
- AC8: recibos RED/GREEN, revisão, limites, hashes e lições persistidos.

## Contrato provisório (refinar após evidência, antes de implementar)
Aplicações HDR/RSIR/VRP devem ter identificação derivada da fonte, não da sigla.
Harness: `plan(app)`, execução local quando viável, `compare`/auditoria quando não.
Saída: status, técnica/backend, resultado, evidências, limitações; sem fatos inventados.
MCP: catálogo e operações equivalentes às do harness, sem acesso arbitrário a rede,
arquivos, credenciais ou shell. Retorno bloqueado para provedor não implementado.

## Limites e estado inicial
Nenhuma licença de reutilização do frontend foi observada; bundles são evidência
privada de análise, não código a redistribuir. Recriação original, não clone pixel
perfect. Sem objetivo de reproduzir hardware quântico ou backend fechado.
Doctor com Python global falhou por `whoosh` ausente; `.venv/bin/python` executou:
16 pass, 6 warn, 0 fail. Usar o ambiente existente, sem instalar pacotes.
Busca web indisponível (HTTP 402); prosseguir com fontes primárias diretas.
Repositório já possui mudanças alheias, inventariadas antes das edições.
