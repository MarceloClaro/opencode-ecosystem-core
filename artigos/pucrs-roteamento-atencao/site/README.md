# Site da dissertação — MIRA

Apresentação editorial e didática da dissertação revista de Marcelo Claro Laranjeira. Interface estática em português, com ilustração SVG animada, laboratório de roteamento, evidências, limites e navegação de apresentação.

**Endereço de publicação previsto:** https://marceloclaro.github.io/opencode-ecosystem-core/

## Uso

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
python3 -m pytest -q tests/test_r781_site_mira.py
```

Abra `http://localhost:8765`. Não é necessário instalar bibliotecas de interface nem executar uma compilação. O módulo do laboratório é `router.mjs`; o Node.js é necessário apenas para os testes funcionais.

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

A especificação é `SPEC-935-R781`; os testes exercitam comportamento do cálculo e casos-limite. A conferência de interface é registrada em `qa.json`. A aprovação do inspetor MIRA e os testes locais não representam validação científica externa.
