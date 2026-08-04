---
spec_id: SPEC-935-R380
title: Enriquecimento do catálogo MASWOS — descrições reais em vez de placeholder
component: agents/catalog/*.md (46 arquivos MASWOS)
status: verified
test_file: tests/test_r380_maswos_catalog_enrichment.py
---

# SPEC-935-R380 — Enriquecimento do Catálogo MASWOS

**Data:** 2026-08-02
**Motivação:** achado colateral registrado ao construir a Seção 6.1 do README
(tabela de 205 agentes): 103 dos 205 registros do catálogo (50%) tinham
`description` placeholder mecânico ("Agente especializado NOME") e corpo
apontando para um caminho Windows externo (`criador-artigo\agents\...`)
inexistente neste checkout — predominantemente o grupo **Catálogo Acadêmico
MASWOS** (46 dos 49 agentes numerados 00–53 com correspondência de arquivo).

**Fonte real localizada:** o diretório irmão
`~/OpenCode_Ecosystem-main/OpenCode_Ecosystem-main/criador-artigo/agents/`
contém os arquivos originais completos (identidade, missão, entradas,
saídas, workflow) que o stub deste repositório apenas referenciava sem
migrar. Este ciclo porta o conteúdo real para dentro do catálogo,
eliminando a dependência de um caminho externo.

## 1. Escopo

Exatamente os 46 agentes MASWOS numerados (00–53, exceto os 3 arquivos
não-agente `DISPATCHER_ATIVACAO`/`README`/`TEMPLATE_HANDOFF`, que
permanecem como achado documentado, não "corrigidos" — não são agentes).
Os demais 54 registros ainda com descrição placeholder (família `reversa-*`,
`auxjuris_*`, ferramental de desenvolvimento genérico, médicos, etc.) **não
fazem parte deste ciclo** — são um achado remanescente documentado na
Seção 4 abaixo, para ciclo futuro.

## 2. Método de migração

Script determinístico (não LLM) que, para cada agente:
1. Localiza `criador-artigo/agents/<id>.md` real.
2. Extrai o título (`# ...`) e as seções do corpo por regex de heading.
3. Deriva a nova `description:` do frontmatter a partir da primeira frase
   da seção de Missão/Identidade/Perfil (nunca inventada — é a frase real
   do autor original, cortada de forma limpa).
4. Reconstrói o corpo do card com todas as seções autorais reais (Missão,
   Identidade, Entradas, Saídas, Workflow, Regras de Atuação, etc.),
   **descartando apenas** seções que apontam para arquivos de referência
   externos não migrados (`Leituras obrigatórias`, `Nome operacional`,
   `Template obrigatório`) — nunca fabrica conteúdo para substituí-las.
5. Preserva o frontmatter A2A já existente no stub (skills/tags/category/
   type) intacto, trocando apenas `description`.
6. Insere nota de proveniência explícita no topo do corpo: card migrado de
   `criador-artigo/agents/<id>.md`, seções de referência externa omitidas
   (não fabricadas).

## 3. Critérios de aceitação

1. Os 46 agentes MASWOS listados não têm mais `description` com o padrão
   "Agente especializado NOME".
2. `load_catalog_definitions()` continua carregando 205 registros sem erro
   (YAML válido em todos os 46 arquivos alterados).
3. Cada arquivo migrado contém a nota de proveniência citando o arquivo-
   fonte real.
4. Nenhum arquivo migrado referencia o caminho Windows externo original
   (`criador-artigo\agents\` com contrabarra, ou `references/*.md`/
   `templates/*.md` do projeto de origem).
5. Zero regressão em `test_sdd_tdd.py` e nos testes de documentação.

## 4. Achado remanescente (fora de escopo deste ciclo)

54 registros continuam com descrição placeholder — a maioria (a família
`reversa-*`, 9 agentes) tem fonte real confirmada em um SEGUNDO diretório
irmão (`~/OpenCode_Ecosystem-main/OpenCode_Ecosystem-main/agents/`, formato
de card OpenCode nativo, distinto do formato MASWOS), mas em formato
estrutural diferente que exigiria um script de migração próprio. Os
demais (`auxjuris_*`, ferramental de desenvolvimento genérico, médicos,
orquestradores, `quantum-nexus-phd`, `PyPISearcher`) não tiveram fonte
real localizada nesta sessão. Candidato a ciclo futuro (R375+).
