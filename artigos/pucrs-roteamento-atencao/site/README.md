# Site da dissertação — MIRA

Apresentação editorial e didática da dissertação revista de Marcelo Claro Laranjeira. Interface em português para leitores sem conhecimento prévio de inteligência artificial, com apresentação interativa do OpenCode Ecosystem Core, analogia em quatro etapas, laboratório com três desafios, questionário com feedback, ilustração animada e navegação de apresentação.

**Site publicado:** https://marceloclaro.github.io/opencode-ecosystem-core/

## Uso

- Explore **O ecossistema**: siga pedido, coordenação, roteador e execução/registro; alterne as perspectivas do projeto, da pesquisa e do MIRA. Setas esquerda/direita e Home/End funcionam dentro dos grupos de etapas e perspectivas.
- Continue por **Entenda**: avance pelas quatro etapas da analogia e acompanhe a equipe ilustrativa.
- No laboratório, conclua três desafios, peça uma pista se necessário e acompanhe suas descobertas. Depois, responda três perguntas com feedback e novas tentativas. O progresso fica apenas na memória da página durante a visita.
- Explore os cenários e os controles de confiança e carga. Ana e Cid partem do exemplo publicado; contexto, Bia e alterações nos controles são didáticos.
- Use **Apresentar** para a navegação guiada. Setas esquerda/direita e Page Up/Page Down mudam de seção; Home/End vão ao início/fim; Esc retorna ao site. As setas dos controles deslizantes continuam alterando seus valores.
- Use **Pausar movimento** para interromper a animação. A interface também respeita a preferência do navegador por movimento reduzido.
- Acesse o deck complementar em `mira/apresentacao/deck.html`.

## Execução real do MIRA

`prepare_mira.py` chama `MarceloClaroOrchestrator.present_task()`. O orquestrador registra `mira-presenter`, delega uma tarefa via Blackboard e executa a esteira `extract → plan → copywrite → build → animate → validate` sobre `mira/manuscrito.md`.

`mira/execucao.json` conserva o identificador da tarefa, resultado, hashes do deck antes/depois da adaptação e ausência de violações do inspetor original. `mira/apresentacao/CONFORMIDADE.md` refere-se ao deck original gerado pelo pipeline. A adaptação acrescenta subtítulos editoriais, tema do site, pausa, retorno, foco visível e suporte a movimento reduzido. A página principal e o laboratório são uma interface específica desenvolvida para esta dissertação; não são saída automática do gerador MIRA.

Para regenerar o deck, no diretório raiz do repositório:

```bash
python3 artigos/pucrs-roteamento-atencao/site/prepare_mira.py
```

## Conferência local

No diretório raiz:

```bash
python3 -m http.server 8765 --directory artigos/pucrs-roteamento-atencao/site
python3 -m pytest -q tests/test_r781_site_mira.py tests/test_r782_aprendizagem_site.py tests/test_r783_ecossistema_site.py tests/test_r784_podcast_site.py
```

Abra `http://localhost:8765`. Não é necessário instalar bibliotecas de interface nem executar uma compilação. O cálculo está em `router.mjs`, e as regras das atividades em `learning.mjs`; o Node.js é necessário apenas para os testes funcionais.

## Proveniência e limites

Fonte científica: [dissertacao-abnt.tex](https://github.com/MarceloClaro/opencode-ecosystem-core/blob/main/artigos/pucrs-roteamento-atencao/dissertacao-abnt.tex), versão editorial publicada no commit `ea00de87b6b8e1e481ddcaaa9b6bc89ea0ebdb5b`.

| Conteúdo | Origem na fonte consolidada |
| --- | --- |
| Máscara, utilidade e normalização | linhas 1560–1845 |
| Exemplo Ana/Cid | linha 545 |
| Bancada principal e comparadores | linhas 2125–2156 |
| Formalização e limites numéricos | linhas 338, 372 e 573 |
| Teste numérico amostral | linhas 346 e 466 |
| Margens exploratórias e agrupamento | linhas 347 e 360–362 |
| Proxy de confiança e correlação | linhas 349 e 547 |

Os resultados são históricos, internos e sintéticos. O laboratório não executa agentes, não reexecuta os experimentos e não mede calibração. A formalização sobre reais não certifica integralmente a implementação numérica. Permanecem as pendências científicas e institucionais documentadas no [relatório da revisão](https://github.com/MarceloClaro/opencode-ecosystem-core/blob/main/artigos/pucrs-roteamento-atencao/revisao-abnt/relatorio_revisao_abnt.md).

## Hospedagem

O código do site reside na branch `main`. Os arquivos estáticos são publicados na branch `codex/gh-pages`, com `.nojekyll`; o GitHub Pages aponta para a raiz dessa branch. Esse fluxo utiliza a [API oficial de GitHub Pages](https://docs.github.com/en/rest/pages/pages). A publicação deve conservar outras pastas e configurações caso uma hospedagem prévia seja encontrada.

As especificações são `SPEC-935-R781`, `SPEC-935-R782` `SPEC-935-R783` e `SPEC-935-R784`; os testes exercitam comportamento do cálculo e casos-limite. A conferência de interface é registrada em `qa.json`. A aprovação do inspetor MIRA e os testes locais não representam validação científica externa.

A revisão didática preserva os números e a fonte científica. Carga alta e indisponibilidade têm comportamentos diferentes; os pesos não são chances de sucesso nem frações da tarefa. A eficácia educacional desta interface ainda não foi medida.

A seção do ecossistema usa `ecosystem.mjs` para o percurso ilustrativo, sem acionar executores. Seu conteúdo deriva de `ARCHITECTURE.md`, `MANUAL.md` e do escopo da dissertação. O MIRA é mostrado como recurso de comunicação, podendo receber encaminhamento direto do coordenador. Nem todo fluxo utiliza o roteador estudado.

## Podcast integrado

A seção **Ouça** usa o áudio real gerado pelo NotebookLM via `MarceloClaroOrchestrator.gemini_notebook_action`, com base na dissertação e em `podcast/fonte-editorial.md`. A duração efetiva é 1355,766712 segundos (22 min 36 s). O arquivo final M4A foi remultiplexado por cópia do fluxo AAC, sem recodificação, para indexar duração e navegação. `podcast/proveniencia.json` contém somente parâmetros, fontes, identificadores e hashes públicos. Recibos internos e credenciais não integram o site.

O áudio começa apenas por ação da pessoa. O player oferece reprodução/pausa, busca, ±15 segundos, velocidade e silenciamento. O elemento nativo permanece disponível quando JavaScript não é executado; o download é uma alternativa independente. A animação decorativa acompanha o estado real de reprodução, sem representar análise da onda sonora, e respeita a pausa global e movimento reduzido.

As três reflexões podem ser exploradas a qualquer momento e levam às atividades existentes. O guia é um resumo editorial das fontes, não uma transcrição literal ou uma lista de capítulos sincronizados. O áudio é divulgação gerada por IA, não um novo resultado científico. Não foi medida a eficácia educacional dessas atividades.

No modo de apresentação, controles do player e da reflexão mantêm seus próprios atalhos. Mudar para outra seção pausa o áudio para evitar reprodução oculta. A apresentação principal passa a ter dez seções; o deck MIRA complementar foi preservado.

Para testar navegação de mídia na prévia, use um servidor HTTP que implemente `Range`/resposta `206`. O servidor simples de Python basta para o texto e reprodução inicial, mas pode limitar a busca no áudio.
