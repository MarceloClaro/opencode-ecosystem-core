---
name: agentes-engenharia-selecao
description: Selecione 10 papéis de engenharia do catálogo wshobson/agents com fonte,
  licença e gate de confiança. Use para descobrir especialistas; não instala 202 agentes,
  não ativa hooks e não transforma catálogo em execução.
metadata:
  round: R1049
  source: https://github.com/wshobson/agents
  license: MIT
  adaptation: Seleção e redação original de 10 papéis inspirados em wshobson/agents
    (commit 7e2fb559cf4b824b27f1fec49fe88f7511066d26); sem cópia de agentes ou comandos.
---

# Agentes de engenharia — seleção

O catálogo original tem 202 agentes, 185 skills e 105 comandos. Aqui há **10
papéis** selecionados por função, com uso e gate. O catálogo é fonte de
descoberta, não prova de qualidade.

## Como selecionar

1. Defina a capacidade necessária e o artefato de saída.
2. Verifique se já existe agente local que cobre o escopo.
3. Leia o contrato do agente original; não copie instruções cegamente.
4. Teste com uma tarefa pequena e permissões mínimas.
5. Registre trust, custo, falhas e lições.

## Lista

Ver `references/agents.json`.

## Limites

Esta skill não copia código, scripts ou hooks do repositório original.

Não há instalação automática, hooks ou marketplace. A seleção não garante
melhor qualidade; o Trust Engine e a revisão humana continuam no comando.
