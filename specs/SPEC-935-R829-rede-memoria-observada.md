---
spec_id: SPEC-935-R829
title: Rede de memória observada no terminal e no painel
component: webapp + marceloclaro
status: proposed
round_id: R829
test_file: tests/test_r829_memory_network.py
---

# R829 — Rede de memória observada

O usuário autorizou o terminal `python -m webapp.memory_network_visualizer`
e a integração no painel Streamlit, com memória, contexto, agentes, evidências,
consulta/resposta e detalhes dos nós. O componente enviado é referência visual;
seu laço bloqueante, cache global e índice de aba inexistente não são preservados.

## Contrato

1. Uma projeção limitada e somente de leitura combina os eventos persistidos do
   MetaBus, memória episódica/semântica, Blackboard da instância primária e os
   grafos de evidências R102/MCI. Dados carregados mantêm origem e IDs.
2. Nós têm tipo, rótulo, origem, instante e relevância opcional. Confiança interna,
   peso de relação e relevância não são convertidos em probabilidade calibrada.
   Ausência é desconhecida; snapshot vazio não fabrica fluxo consulta→resposta.
3. A animação indica eventos efetivamente observados, com expiração da ativação;
   histórico não se torna evento novo a cada atualização. A janela temporal,
   truncamento e fontes indisponíveis ficam explícitos. O observador não escreve
   no grafo científico, não executa agentes, nem inicia modelos.
4. Modo demonstrativo é separado e identificado em todo frame, sem contaminar
   as fontes reais. Layout e seleção são determinísticos e têm quotas de nós,
   arestas, eventos, texto e leitura de arquivo; arquivo parcialmente escrito,
   removido, rotacionado ou inválido não bloqueia o painel.
5. Terminal tem saída única/JSON e frames finitos para execução automatizada;
   TTY permite atualização animada e cancelamento por teclado. Texto externo
   não injeta controles de terminal. A implementação não requer Streamlit.
6. A aba web é realmente criada e usa atualização não bloqueante na thread
   Streamlit, estado de demonstração por sessão, filtros, seleção e detalhes.
   O grafo da pesquisa profunda é conservado entre reruns e reutilizado pelo
   browser existente. HTML/JS externo é inerte; há controle de movimento.
7. O mesmo snapshot alimenta ambas as apresentações. Uma entrada somente de
   leitura no orquestrador primário fornece o estado ao painel, sem delegação
   direta a agentes. CLI dedicado observa o estado persistido do projeto.
8. Resumos de diagnose declaram corpus, escopo local e limitações: categorias
   detectadas não certificam disponibilidade; SPS/CR não certificam correção;
   scores não calibrados não são percentuais de eficácia. Gaps vazios não
   apagam categorias ausentes, e licença ausente continua sem licença declarada.

## Aceite

- Testes RED antes da implementação e GREEN sobre fontes reais temporárias,
  IDs/arestas, expiração, truncamento, JSON inválido, isolamento de demonstração,
  argumentos CLI, saída sem TTY, controles de terminal e conteúdo HTML adverso.
- Testes de integração com o grafo público R102 e com eventos reais do MetaBus
  em diretório isolado; abrir a visualização não modifica os arquivos de origem.
- Execução CLI real e inspeção funcional do painel em navegador, com movimento,
  parada, seleção e retorno a dados locais. Simulação é identificada como tal.
- Doctor anterior à edição: 22/22 em `outputs/core-r820/doctor-before-r829.json`.
- Evidências em `outputs/core-r829/`; suíte ampla e evolução consolidadas depois.

## Limites

A consulta opcional de memória é uma busca lexical explícita, coordenada pelo
primário e registrada como `memory.query`, `memory.retrieved` e `memory.response`.
Não sintetiza resposta por LLM nem calcula probabilidade. O painel deve tolerar
score não registrado no ledger e substituir contagens antigas fixas por
inventários atuais, com rótulos que não confundam arquivos com testes aprovados.

É uma rede visual de registros do Core; não revela pesos ou atenção interna de
um LLM. Eventos não persistidos não podem ser observados por outro processo.
Janela de eventos e seleção têm limites declarados; não há garantia de cobertura
integral, validação externa ou execução de todos os agentes.

## Fidelidade do grafo exportado no browser existente

As referências de evidência de entidades/relações, identificadores, pesos reais
(incluindo zero e 2,5), direção, metadados, conteúdo e instante são preservados
na exportação pública e na reidratação. O browser não usa criação de entidades
para reconstruir IDs, não substitui zero por 1,0 e não gera fragmentos ausentes.
Referências compartilhadas contam uma única evidência por ID. Duplicatas
conflitantes de um mesmo ID são rejeitadas; registros antigos sem referências
explícitas declaram vínculo desconhecido. Contagens antigas não permitem inferir
quais evidências sustentam uma entidade. Um fragmento ausente permanece como
referência não resolvida, sem conteúdo criado. Peso não é confiança calibrada.

Aceitação específica em `tests/test_r829_evidence_roundtrip.py`: grafo real
BRAF→Vemurafenib com três evidências preservadas, casos negativos, imutabilidade
da entrada e compatibilidade com exportações antigas. RED/GREEN em
`outputs/core-r829/evidence-roundtrip/`. Nenhum resultado constitui validação
clínica ou externa da relação exemplificada.
