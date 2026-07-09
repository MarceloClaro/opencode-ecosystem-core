<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# MASWOS V4 - Arquitetura de Ecossistema Integrado (Módulos de Pesquisa, Validação, Correção e Avaliação)

A nova versão (V4) do Multi-Agent Scientific Writing Operating System introduz um modelo de **Ecossistema Fechado de Iteração Contínua**. O objetivo é garantir que nenhuma fase seja concluída sem atingir a pontuação máxima (10/10) nos critérios Qualis A1 e internacionais.

## 1. Módulo de Pesquisa Profunda (Deep Research Module)
Responsável por garantir a rastreabilidade, cobertura e atualidade da literatura e dados.
- **Agentes Integrados:** A2 (Busca e Curadoria), A3 (Evidências), A35 (Coleta de Dados Reais), A43 (Bases Especializadas).
- **Melhoria V4:** O Módulo de Pesquisa agora atua de forma contínua, sendo reacionado sempre que o Módulo de Validação apontar lacunas teóricas ou empíricas. Ele constrói o `log_busca.md` de forma dinâmica.

## 2. Módulo de Validação Cruzada (Cross-Validation Module)
Responsável por garantir que todas as afirmações, citações e dados estejam perfeitamente alinhados e justificados.
- **Agentes Integrados:** A14 (Consistência Interna), A12 (Auditoria ABNT), A33 (Multi-Norma), A19 (Auditoria de Código).
- **Melhoria V4:** Validação linha a linha (Line-by-Line Auditing). Nenhuma afirmação é aceita sem um "lastro documental" rastreável. Se houver falha, o trecho é enviado automaticamente ao Módulo de Correção.

## 3. Módulo de Correção Ativa (Active Correction Module)
Um novo conceito na V4. Em vez de apenas apontar erros, este módulo corrige ativamente e reescreve os trechos que não atingiram 10/10.
- **Agentes Integrados:** A44 (Novo: Agente de Correção Textual Qualis), A45 (Novo: Agente de Refinamento de Argumentação).
- **Melhoria V4:** Quando o A13 (QA Qualis) ou A14 (Consistência) reprovam um trecho, o Módulo de Correção atua para reescrever mantendo o rigor e a densidade (estrutura de 6 frases por parágrafo).

## 4. Módulo de Avaliação Iterativa (Iterative Evaluation Module)
Responsável pelo "Stress Test" final e pela garantia da nota 10/10.
- **Agentes Integrados:** A13 (QA Qualis A1), A31 (Blind Peer Review Emulado), A29 (Conformidade Internacional).
- **Melhoria V4:** O processo agora é um **Loop de Avaliação**. O texto só sai do loop quando o A31 e o A13 derem pontuação máxima em todos os critérios da `rubrica_avaliacao.md`.

## Fluxo de Integração V4 (Loop Iterativo)

1. **Geração (Módulo de Pesquisa + Redação)** -> Cria o rascunho inicial do capítulo/seção.
2. **Validação (Módulo de Validação)** -> Verifica consistência, ABNT, citações, e densidade.
3. **Avaliação Parcial (Módulo de Avaliação)** -> Avalia contra a rubrica (ex: nota 7/10).
4. **Correção (Módulo de Correção)** -> Reescreve e ajusta as falhas apontadas para subir a nota.
5. **Re-Avaliação** -> Repete os passos 2-4 até atingir 10/10.
6. **Aprovação do Editor-Chefe (A0)** -> Libera a fase.

Este modelo garante que a qualidade seja intrínseca ao processo de produção, e não apenas uma verificação final.
