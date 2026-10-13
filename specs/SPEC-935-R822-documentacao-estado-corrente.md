---
spec_id: SPEC-935-R822
title: Estado documental corrente sem apagar checkpoints históricos
component: documentation
status: implemented
round_id: R822
test_file: tests/test_r822_documentation_current_state.py
---

# SPEC-935-R822 — Estado documental corrente

## Problema demonstrado

O gate R448 falhou na segunda execução integral: o catálogo passou a conter
255 agentes, mas os cinco guias operacionais ainda declaravam 254. O badge
do README indicava 15 MCPs; a arquitetura listava 11 MCPs e 238 agentes como
se fossem correntes. O checkpoint PROGRESS se apresentava como estado atual
apesar de terminar na R414, de 13/08/2026. Contagens históricas explicitamente
datadas e o conteúdo científico desse checkpoint precisam ser preservados.

## Requisitos

1. R822.1: manter evidências RED e GREEN em `outputs/core-r822`; executar
   doctor antes de editar. O gate integral interrompido não recebe estado GREEN.
2. R822.2: um gerador local deriva agentes, MCPs e comandos de `opencode.json`
   e a quantidade de checks do diagnóstico estrutural. Atualiza somente blocos
   delimitados nos sete guias README, MANUAL, ARCHITECTURE, CLAUDE, PROGRESS e
   instaladores comum/Windows; publica a lista completa de MCPs na arquitetura
   e mantém as contagens do diagrama operacional do README no mesmo inventário.
3. R822.3: modo de conferência retorna divergências sem escrever; repetição
   após sincronizar é idempotente. Marcadores ausentes, duplicados ou invertidos
   interrompem a operação antes de escrever qualquer documento.
4. R822.4: alterações de cardinalidade e nomes na configuração se refletem
   nos blocos e na lista MCP. A ordenação da lista é determinística e não
   representa disponibilidade, autenticação, inferência ou validação externa.
5. R822.5: remover contagens operacionais repetidas fora dos blocos, preservando
   snapshots explicitamente históricos. O registro R596 conserva seu total
   como dado histórico; a validação antiga R448 não é apresentada como a última.
6. R822.6: PROGRESS recebe orientação corrente de retomada e conserva
   integralmente o conteúdo anterior dentro de uma seção histórica identificada.
   CLAUDE aponta para a seção corrente, sem induzir retomada automática da R414.
7. R822.7: o gerador documental não altera livro, catálogos, integrações funcionais,
   configuração, resultados científicos nem evidências históricas. O inventário do livro será
   reconciliado na consolidação posterior se novas specs alterarem seu total.
8. R822.8: o link ao README principal no guia Hugging Face resolve para o arquivo
   da raiz. A verificação rápida do guia nano executa um preview local real,
   sem depender de um `--help` sem handler e sem chamar servidor ou modelo.

## Aceite

- R448, R449, R455 e R822 passam no escopo documental aplicável.
- Reexecução do gerador em modo de conferência não identifica divergência.
- Duas execuções não mudam os bytes dos documentos.
- A preservação integral do PROGRESS anterior é conferida por hash e recibo.
- A suíte geral e os ciclos de evolução serão consolidados pelo agente principal;
  nenhum resultado externo é inferido desses controles internos.


## Evidência de aceite local — 12/10/2026

- Doctor anterior às edições: 21 checks aprovados em 11/10; nova conferência
  estrutural em 12/10 também passou. R824 acrescentou depois o check do
  navegador; o gerador passou a derivar **22 checks**, sem fixar esse número
  na implementação.
- RED documental e do gerador: 9 falhas e 5 aprovações; RED adicional recusou
  corretamente a implementação que não tratava configuração lista/nula
  (2 falhas por AttributeError antes da correção).
- GREEN de R822/R448/R449/R455/R129/R640-truthfulness: **38 testes aprovados**,
  sem falhas, erros ou skips, em `outputs/core-r822/green.xml` e `.txt`.
- O comando real de conferência encerrou com código zero e nenhuma divergência.
  Duas sincronizações consecutivas preservaram os hashes dos sete guias.
- Três mutações isoladas foram rejeitadas: cardinalidade errada de agentes,
  escrita indevida no modo de conferência e aceitação de marcador duplicado.
  Nenhuma fonte operacional foi modificada na execução dessas contraprovas.
- Os **77.096 bytes** do PROGRESS anterior permanecem idênticos dentro do
  arquivo histórico; seu hash consta em `outputs/core-r822/release-summary.json`.
  A orientação corrente aponta para fontes e contratos em vez de apresentar
  a R414 como último estado. Snapshots datados e provas científicas não foram
  removidos.
- O aceite acima é documental e operacional local. A suíte geral e a evolução
  permanecem sob consolidação do agente principal; provas externas não são
  inferidas desse escopo.

## R822.9 — Assets locais explicitamente citados no livro

Na reconciliação do livro, o inventário de `fontecore` conserva os hashes dos
arquivos citados diretamente e inclui recursivamente os arquivos de diretórios
explicitamente citados, inclusive PNG/PPTX/JSON e manifestos. A ordenação é
determinística e as contagens existentes não mudam por essa inclusão. Somente
assets resolvidos dentro do workspace são lidos; diretórios filhos simbólicos
não são percorridos, evitando ciclos e saídas da raiz. O aceite adicional usa
fixtures temporárias em `tests/test_r814_livro_reconciliado.py` antes de qualquer
geração real e não promove esses assets a validação científica externa.


## R822.10–11 — Capa e legibilidade executável do PDF

A capa inclui Core no título e explicita validação computacional no subtítulo,
padronizados com a folha de rosto. O retrato original é preservado; o JPEG
exportado em 300 dpi não recebe alegação de detalhe fotográfico recuperado.
A inspeção visual reproduziu rótulos brancos sobre painéis claros no diagrama
arquitetural e comandos sem espaços na extração do PDF. Os helpers de código
conservam espaços por opção do pacote url, verificada com compilação real e
extração de texto em test_r814_livro_reconciliado.py. Rótulos e setas do diagrama
usam contraste adequado ao fundo, mantendo texto branco só no nó escuro.
O aceite exige nova compilação, gates editoriais e inspeção da mesma seleção;
o PDF defeituoso e o teste RED permanecem arquivados.

Nomes de arquivos nos helpers verbatim usam underscore literal, conservando
o escape apenas fora desses helpers. O comando do inventário é compilado e
extraído diretamente da fonte real no teste de reprodução. Os geradores do
catálogo e do inventário compartilham a correção; não dependem de edição manual
dos módulos gerados.
