# RED → GREEN → REFACTOR

- **RED:** escreva o menor teste que expressa o contrato e veja-o falhar.
- **GREEN:** implemente o mínimo; não antecipe requisitos.
- **REFACTOR:** só com verde; preserve o comportamento.
- **EVIDÊNCIA:** salve comando, retorno e diff. Um resumo sem saída não é prova.

Checklist: teste falha pelo motivo certo; implementação não altera o teste;
regressão passa; não há `skip` silencioso; o teste não depende de rede.
