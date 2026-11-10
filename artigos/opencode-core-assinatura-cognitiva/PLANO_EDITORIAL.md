# Plano editorial — artigo "A casa que ajuda a pensar"

**Status:** rascunho 1.0, para revisão humana.
**Data:** 10 de novembro de 2026.
**Natureza:** entrega editorial, não funcionalidade de runtime. Não altera código, specs de runtime nem o registro de evolução.

## 1. Objetivo

Produzir um artigo ensaístico-acadêmico que analise o OpenCode Ecosystem Core
como uma prótese cognitiva concebida por seu próprio usuário, articulando:

- a orquestração e a arquitetura agênticas do sistema;
- a noção de assinatura cognitiva autoral, definida como configuração situada
  de escolhas documentáveis;
- o contexto relatado de altas habilidades/superdotação (AH/SD) e risco de
  Alzheimer do criador, tratado como condição de projeto — não como diagnóstico,
  prognóstico ou alegação de eficácia.

## 2. Público

Pesquisadores de cognição distribuída, arquitetura de software, sistemas
multiagente, educação especial e saúde; leitores do repositório; avaliadores
interessados em estudos de caso de tecnologia assistiva autoral.

## 3. Tese

O Core não é apenas uma ferramenta de produtividade. É uma prótese cognitiva
autoral: externaliza memória, função executiva, atenção e verificação, e
materializa um estilo de decisão marcado por desconfiança produtiva da própria
memória, primazia do contrato, verificação contra a própria convicção,
arquitetura da interrupção e vocação didática. Essa assinatura é documentável,
mas não é biomarcador, teste de personalidade ou prova de consciência. O sistema
pode ajudar o criador a sustentar continuidade e agência; não previne, trata ou
diagnostica Alzheimer. Seu valor depende de preservar vínculo social,
contestabilidade e limites explícitos.

## 4. Estrutura

1. Introdução: a ferramenta que nasce de uma falta.
2. O caso e o método: estudo de caso documental, posição do autor, limites.
3. O usuário-criador: AH/SD, assincronia e risco de Alzheimer.
4. De andaimes a próteses: cognição estendida, artefatos, carga e reserva.
5. A arquitetura do Core: o ciclo P→E→D→E→V→R em seis movimentos.
6. A assinatura cognitiva: cinco marcas documentáveis.
7. O que a prótese faz — e o que ela não faz.
8. Riscos, efeitos adversos e salvaguardas.
9. Como saber se funciona: protocolo de avaliação N-of-1.
10. Discussão: a casa, o arquiteto e o tempo.
11. Conclusão.
12. Referências.
13. Apêndice A: evidências e contagens.
14. Apêndice B: checklist de verificação editorial.

## 5. Critérios de aceitação

- **CA01.** Título, resumo, abstract e palavras-chave em português e inglês.
- **CA02.** Tese explícita e retomada na conclusão.
- **CA03.** Definição operacional de "prótese cognitiva autoral" e de
  "assinatura cognitiva".
- **CA04.** Descrição da arquitetura com evidência de arquivos e contagens
  datadas.
- **CA05.** Tratamento não clínico de AH/SD e risco de Alzheimer; distinção
  entre relato, risco, diagnóstico e prevenção.
- **CA06.** Nenhuma alegação de cura, prevenção, tratamento, diagnóstico,
  validação externa ou superioridade.
- **CA07.** Seção de riscos e efeitos adversos, incluindo dependência,
  sobrecarga, viés de automação e burocratização do cuidado.
- **CA08.** Protocolo de avaliação N-of-1, pré-registrado e com supervisão
  clínica, com desfechos e limites.
- **CA09.** Referências reais e verificáveis; DOIs conferidos quando houver.
- **CA10.** Contagens de configuração acompanhadas de ressalva de que não
  provam disponibilidade, autenticação, inferência ou validação.
- **CA11.** Nota de uso de IA e de revisão humana pendente.
- **CA12.** Distinção entre fontes primárias do repositório e literatura
  externa.

## 6. Fontes primárias

- `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `MANUAL.md`, `CORRIGENDUM.md`.
- `docs/PREFACIO_ASSINATURA_COGNITIVA_R909.md` e
  `specs/SPEC-935-R909-prefacio-assinatura-cognitiva.md`.
- `mci/metabus.py`, `mci/blackboard.py`, `mci/task_runtime.py`,
  `mci/reflexion.py`, `mci/metacognitive_evaluator.py`,
  `mci/metacognitive_gate.py`.
- `sdd/spec_engine.py`, `sdd/tdd_runner.py`, `sdd/tdd_history.py`.
- `trust/trust_engine.py`, `trust/behavioral_gate.py`,
  `economy/token_economy.py`.
- `evolution/cycles.py`, `evolution/cycles.json`.
- `opencode.json`, `marceloclaro/orchestrator.py`, `marceloclaro/doctor.py`.
- `livro-core/mod-00-capa.tex` (prefácio R909).

## 7. Verificação

- Conferir contagens no checkout de 10/11/2026 e datar a divergência em relação
  ao bloco reconciliado do `README.md`.
- Conferir títulos e DOIs das referências externas.
- Verificar se o artigo não contém linguagem de diagnóstico, cura, prevenção
  ou validação externa.
- Verificar se cada afirmação sobre o código tem arquivo de referência.
- Contar palavras e seções.
- Revisão humana independente permanece pendente.

## 8. Riscos editoriais

- **Overclaim médico:** confundir risco com diagnóstico ou prótese com
  tratamento.
- **Privacidade:** expor detalhes de saúde além do relato autorizado.
- **Autocelebração:** transformar análise arquitetural em propaganda.
- **Viés de confirmação:** selecionar apenas evidências que confirmem a tese.
- **Alucinação de fontes:** citar obras ou DOIs inexistentes.
- **Fetichização da assinatura:** tratar a metáfora como prova de mente.

## 9. Estado

Rascunho redigido. Pendente: revisão do autor, conferência final de DOIs,
revisão de língua e eventual compilação em PDF/DOCX.
