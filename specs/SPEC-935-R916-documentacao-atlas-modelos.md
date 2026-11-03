---
spec_id: SPEC-935-R916
title: Documentação operacional, atlas atual e seleção econômica de modelos
version: 1.0.0
status: draft
test_file: tests/test_r916_documentation_atlas.py
---

# SPEC-935-R916 — documentação e atlas do Core

## Objetivo e escopo

Revisar README, manuais, onboarding, índice documental e mapas contra as fontes
atuais. Preservar modificações locais, arquivos de domínio, livro e recibos
históricos. Não restaurar componentes R913/R914 removidos pelo operador.
Registrar configuração, instalação, autenticação, inferência, aceite e validação
externa como estados diferentes. Documentar NotebookLM 0.15.6, plugins locais,
metacognição, agentes, CI local, grafos e autenticações separadas.

O usuário acrescentou a comparação de modelos ChatGPT/OpenAI e Gemini/Google
para economia. Consultar fontes primárias e catálogo local; separar preços de
API, créditos e franquias de assinatura. Não mudar o provedor padrão nem
declarar economia medida sem ensaio comparável e critério de qualidade.

## Extração das fontes

Preservar o modo Git determinístico de R879. Acrescentar `--source worktree`
com ref-base explícito: ler somente fontes de produção versionadas e
`opencode.json`; omitir removidos e nunca seguir symlinks ou submódulos.
Fontes não rastreadas e credenciais privadas não entram na coleta. O índice
das demais categorias usa metadados do commit-base, claramente identificado,
para evitar circularidade dos próprios artefatos gerados.

Registrar hashes dos bytes analisados, modificações, exclusões e identidade
da coleta. Conferir novamente as fontes ao terminar; mudança concorrente
invalida a extração. Links de código modificado localmente não podem se
apresentar como permalinks do commit-base. O grafo AST continua descrevendo
imports declarados, sem provar ligação funcional ou execução.

## Aceitação

1. RED em `tests/test_r916_documentation_atlas.py` antes do novo modo; GREEN
   deve demonstrar inclusão de modificações, exclusão de removidos, recusa de
   mudança concorrente, preservação de índice Git e não leitura de symlinks ou
   não rastreados. A regeneração documental não deve invalidar a própria coleta.
2. Inventário, DOT/SVG, Mermaid e manifesto conservam todos os módulos e pares;
   testes comparam conjuntos independentemente, sem números históricos fixos.
3. Todos os fluxos do catálogo estão completos no README e no visualizador,
   com legenda, limites, SVG e âncoras de código válidas da origem declarada.
4. Guias operacionais convergem nas contagens atuais; versões anteriores e
   suas evidências permanecem históricas. Não promover o R914 parcial nem os
   recibos Lean anteriores a prontidão das fontes atuais.
5. Executar verificações de regeneração, testes relevantes, links locais e
    renderização real. Inspecionar a página e diagramas representativos; registrar
    falhas e limites. Não é revisão científica externa ou garantia de produção.

6. O guia de modelos declara os IDs efetivamente presentes no catálogo do checkout,
   distingue o modelo da sessão de `opencode.json`, tarifas de API de assinatura,
   tiers/cotas e preço por tarefa aceita. GPT-6 Luna e Gemini Flash são candidatos,
   não ganhadores de benchmark. Não troca `default_agent` nem `model` em silêncio.
7. O fluxo de contexto local documenta Ollama, janelas declaradas versus runtime,
   custos de retry e a diferença entre tokens medidos pelo provider e estimativas.
   429/quota não dispara fallback oculto.
8. DOT, Mermaid, README e visualizador exibem a origem do desenho: commit-base,
    identidade SHA do worktree, contagem de modificados/removidos e limites de
    permalinks. Âncoras de fonte são atualizadas apenas a partir do manifesto
    worktree revalidado; removidos, symlinks e não rastreados não entram.
   O HTML gerado inclui o SHA-256 do template que realmente o produziu.
9. A pesquisa de quantização no GitHub fixa commit, licença do código e função;
    distingue runtime, conversão/quantização e treinamento/exportação. Não clona,
    instala, baixa weights, executa benchmark nem promove compatibilidade a qualidade.

## Evidência de implementação

Recebidos anteriormente: recibos históricos da versão 21 fluxogramas/76 testes.
Eles não atestam a revisão atual. A execução GREEN desta extensão, renderizações
dos 22 fluxos, âncoras/worktree SHA, testes de regressão e verificação de
renderização permanecem pendentes até serem executados e reconciliados com os
artefatos atuais. Não foi alterado o modelo padrão; não foi executado benchmark
de qualidade, quantização, clone ou download de pesos.
