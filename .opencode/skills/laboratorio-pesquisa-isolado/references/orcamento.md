# Orçamento

O budget limita passos, segundos, custo e chamadas externas. Cada consumo é
registrado. Excesso levanta `BudgetExceeded` e interrompe o passo; não há
"ajuste" silencioso. Custo zero é o padrão; qualquer custo precisa de
autorização explícita.
