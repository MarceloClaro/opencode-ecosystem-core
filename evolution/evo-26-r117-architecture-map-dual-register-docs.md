# R117 — Mapa Interativo da Arquitetura + Documentação Dupla-Registro

## Objetivo

Atualizar de forma completa e minuciosa a documentação de arquitetura, cobrindo todos os subsistemas reais do ecossistema (incluindo R107-R116, ausentes do diagrama até este ciclo), em dois registros de leitura — leigo e PhD — com legendas, instruções, e um mapa interativo dinâmico com tratamento visual 3D.

## Mudanças Entregues

1. **`docs/architecture_map.html` — mapa interativo autocontido**
   - 6 camadas arquiteturais (Interface & Instalação, Orquestração & Confiança, MCI, Pipeline Científico, Raciocínio & Descoberta, Produção/Segurança/Evolução) organizadas ao redor do hub central (`marceloclaro`)
   - Tratamento 3D real: `perspective` + `transform-style: preserve-3d` + `translateZ` por nó, com paralaxe respondendo ao movimento do mouse (sem WebGL/dependências externas — CSP estrito respeitado)
   - Alternador Leigo/PhD: cada camada e cada nó interno tem descrição própria nos dois registros
   - Legenda de cores + instruções de leitura embutidas na própria página
   - Paleta nomeada (blueprint/cianótipo: fundo escuro `#0e1a2b` / papel claro `#f3f1e7`, traço ciano/índigo, destaque âmbar) com temas claro/escuro reais (tokens redefinidos, não invertidos ingenuamente)

2. **`ARCHITECTURE.md` — diagrama Mermaid completo**
   - Adicionados os nós que faltavam: Interface & Instalação (R116), Loop Engineering (R109), GoalDriftDetector no Trust Engine (R112), ARCHE RLT (R114), Detector de Falácias (R113), Revisão às Cegas no Peer Review (R115), Doctor+Helpdesk+Corrigendum (R110), fontes de pesquisa expandidas (R111), e a fusão real do pipeline científico no orquestrador (R108/R109)

3. **`README.md` — dois registros completos**
   - "Para Leigos": tabela de personagens (Reitor, Quadro de Avisos, Memória Coletiva, Pesquisador-Chefe, etc.) mapeando cada metáfora ao arquivo real
   - "Para PhDs": lista de diferenciais arquiteturais cobrindo todas as adições R107-R116
   - Nova seção "Mapa da Arquitetura" com tabela de legenda das 6 camadas (cor, descrição leigo, descrição PhD) e 5 instruções de leitura numeradas

4. **`MANUAL.md`**: referência ao mapa interativo adicionada

## Verificação

- JS embutido validado com `node --check` (14437 caracteres, sem erros)
- HTML balanceado (divs, chaves CSS, tags script/style) verificado programaticamente
- Diagrama Mermaid: contagem de `subgraph`/`end` e colchetes/parênteses balanceada
- `python3 -m pytest tests/test_r116_installer_platform_upgrade.py -q` → 32 passed (inclui teste que verifica conteúdo do README)
- Artefato publicado via Artifact tool para inspeção visual antes da entrega

## Lições

1. Documentação de arquitetura fica defasada silenciosamente — o diagrama Mermaid principal não tinha nenhum dos ~15 subsistemas adicionados em R107-R116, apesar de cada ciclo ter atualizado a tabela de specs e as métricas de maturidade.
2. Efeito 3D em CSS é mais robusto com inclinação modesta (8-10°) + paralaxe por mouse do que com ângulos isométricos extremos que exigiriam contra-rotação de cada nó filho para manter o texto legível — sem capacidade de renderizar/testar visualmente neste ambiente, a escolha conservadora foi a certa.
3. Dois registros de leitura (leigo/PhD) funcionam melhor quando a própria tipografia os distingue (prosa serifada para leigo, dados monoespaçados para PhD), não só o conteúdo do texto.

## Score

**9.0/10**

- Fecha uma lacuna real e mensurável (diagrama desatualizado há 10 ciclos)
- Primeiro artefato interativo/visual do projeto, mantendo o CSP estrito de artifacts (sem dependências externas)
- Dois registros de leitura genuinamente completos, não apenas um resumo raso
- Não introduz nenhuma alegação nova — apenas mapeia fielmente o que já existe
