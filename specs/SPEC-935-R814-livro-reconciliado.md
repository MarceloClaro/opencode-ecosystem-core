---
spec_id: SPEC-935-R814
title: Reconciliação editorial e reprodução do livro Core
component: livro-core
status: implemented
round_id: R814
test_file: tests/test_r814_livro_reconciliado.py
---

# SPEC-935-R814 — Livro reconciliado

## Problema demonstrado

A execução geral apresentou 18 falhas nos gates R617–R620. O catálogo
publicado anuncia 248 agentes enquanto a configuração atual declara 254.
As leituras guiadas usam formas didáticas diferentes e o inventário de
citações conserva números de uma edição anterior. Alguns diagramas já têm
explicação substancial, mas outros carecem de mecanismo, justificativa,
limite e fonte. O injetor R613 pode duplicar uma seção existente cujo marcador
foi perdido. Fontes e geradores do livro são idênticos a HEAD nessa auditoria.

## Requisitos

1. R814.1: reproduzir RED nos gates editoriais e conservar evidências em
   `outputs/core-r814`, sem alterar configuração, MCP, CLI ou scanners.
2. R814.2: gerar o catálogo pela fonte autoritativa `gen_mod10.py`, mantendo
   fichas, permissões, nomes em português e distinção entre registro e execução.
3. R814.3: o gerador de ativação preserva uma seção revisada já existente,
   reconcilia sua proveniência e não duplica conteúdo em reexecuções. Quando
   uma revisão substituiu o título e o conteúdo da antiga seção, aposenta-se
   o marcador R613 para um controle R814 explícito, sem reaplicar o template.
   Se precisar criar uma seção nova, a citação possui os seis campos da macro
   real, incluindo autoria/localizador, conforme regressão RED específica.
   O catálogo identificado como arquivo gerado pertence integralmente a
   `gen_mod10.py`: o injetor não acrescenta conteúdo que esse gerador perderia.
4. R814.4: um inventário reproduzível deriva agentes, MCP, comandos, specs,
   testes, referências e chamadas de citação dos arquivos atuais. A fonte e
   o escopo de cada contagem permanecem explícitos; números históricos ou
   hipotéticos não são convertidos em medidas atuais.
5. R814.5: cada módulo pedagógico contém pergunta, definições, método,
   exemplo resolvido, verificação, limite e exercícios substanciais. Nenhum
   bloco é acrescentado apenas como marcador vazio ou alegação de qualidade.
6. R814.6: cada diagrama explica suas setas, sua razão de organização e seu
   limite. Fontes primárias do código sustentam descrições locais; literatura
   externa sustenta apenas as analogias e alegações que lhe correspondem.
   O gate aceita uma fonte local identificável e realmente existente, sem
   exigir um DOI decorativo para um diagrama da implementação.
7. R814.7: uma alteração no contrato literal de um gate conserva ou amplia
   o requisito semântico, recebe justificativa nesta spec e teste de rejeição
   de fonte ausente. Não há skip, afrouxamento de limite ou retorno a texto
   científico incorreto para obter GREEN.
8. R814.8: compilar em WSL, renderizar e inspecionar cada capítulo alterado,
   incluindo o catálogo e seus exemplos. Entregar fonte e PDF atualizado,
   relatando warnings e escopos não verificados, sem certificação externa.
9. R814.9: o inventário acompanha novos perfis adicionados ao catálogo. Um
   número historicamente incorreto pode tornar-se o total corrente; o gate
   R618 deriva essa distinção da configuração e mantém a rejeição de totais
   antigos divergentes. Frações com denominador obsoleto também são recusadas
   por uma expressão que reconhece dígitos reais, com contraprovas R814.
   Preservam-se medições históricas apenas dentro de um bloco de resultado
   identificado como retrato histórico, com data e referência ao inventário
   corrente. Texto sem essas três condições não recebe essa exceção.

## Aceite

- R617, R618, R619, R620 e R814 passam após geração reproduzível.
- Duas execuções dos geradores preservam o mesmo conteúdo.
- `latexmk` conclui, o PDF tem texto e páginas válidas e as imagens dos
  capítulos alterados são inspecionadas.
- Nenhuma inferência, validação clínica ou eficácia do Core é inferida do
  inventário, de uma fórmula didática ou de uma compilação sem erro.


## Evidência de conclusão — 11 de outubro de 2026

- Gate editorial final: **70 testes aprovados**, sem falhas, erros ou skips;
  evidências em `outputs/core-r814/editorial-close.txt` e `.xml`.
- Os geradores foram executados duas vezes e produziram conteúdo idêntico;
  `outputs/core-r814/generation-reproduction.json` registra os hashes.
- O inventário corrente preserva o novo perfil 54 e deriva **255 agentes,
  16 servidores MCP, 30 comandos, 480 specs (390 da série R), 355 arquivos
  de testes R, 14 referências, 83 chamadas de citação e 13 fichas condensadas**.
  São contagens das fontes, sem inferência sobre execução ou eficácia.
- Compilação limpa concluída em WSL: **348 páginas A4**, 5.873.376 bytes;
  SHA-256 `423feb56c133ff7b1c1a6ce9ec2fdd6c8ba68858accef6552a2e920dd4d8f8ab`.
  O PDF de entrega é `output/pdf/opencode-ecosystem-core-revisado.pdf` e
  conserva o mesmo hash de `livro-core/main.pdf`.
- Foram renderizadas e inspecionadas **138 páginas**, reunidas em 18 contatos,
  cobrindo os 25 módulos alterados, 37 diagramas e 25 leituras guiadas;
  páginas críticas também foram examinadas individualmente. O manifesto
  preserva os hashes das imagens e do PDF em `outputs/core-r814/render-manifest.json`.
- A página física 285 delimita a medição de 29/09/2026 (R608–R609), conserva
  201/212 e 212/212 como denominadores históricos, informa o inventário
  corrente de 255 agentes e explicita a ausência de reexecução dessa medição.
  Houve também inspeção independente dessa página e de quatro contatos.
- Avisos remanescentes: **19 Underfull hbox** e **1 depreciação de idioma
  brazil pelo babel**. Não houve Overfull, float excessivo, referência
  indefinida, erro fatal ou NUL no log final. Não se observaram cortes nem
  sobreposições nas páginas inspecionadas; as demais 210 páginas não foram
  renderizadas nesta seleção. O aceite é operacional e editorial, sem
  validação científica externa.
- Fontes TeX, geradores e testes permaneceram iguais ao congelamento final;
  somente o status e esta evidência documental foram acrescentados à spec.
