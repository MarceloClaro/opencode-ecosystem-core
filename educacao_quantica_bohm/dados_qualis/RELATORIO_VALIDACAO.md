# Validação do estudo de VQC com ruído benéfico

Réplica crítica com 2 e 4 qubits, validação cruzada estratificada de 5 folds
e intervalo de confiança bootstrap de 95%. A métrica é acurácia de teste.

| n | Configuração | Acurácia teste | Desvio | IC95 |
|---:|---|---:|---:|---|
| 2 | baseline | 0.927 | 0.064 | [0.882, 0.972] |
| 2 | phase_005 | 0.927 | 0.064 | [0.882, 0.972] |
| 2 | phase_010 | 0.927 | 0.064 | [0.882, 0.972] |
| 2 | depol_005 | 0.927 | 0.064 | [0.882, 0.972] |
| 2 | amp_005 | 0.927 | 0.064 | [0.882, 0.972] |

## Leitura crítica

- O relatório original usa **5 trials** e um **único split 50/20**; isso
  não permite afirmar significância estatística nem generalização.
- A comparação de arquiteturas com **um único trial** por configuração
  (hardware efficient = 81,0%) não sustenta “superioridade estatística”.
- O rótulo “primeira aplicação documentada” não é verificável sem uma
  revisão sistemática; a literatura de VQC + Optuna é ampla.
- O efeito de ruído benéfico, se existir, precisa sobreviver a:
  mais folds, mais seeds, mais datasets, intervalo de confiança e
  validação em hardware. Esta réplica testa os dois primeiros pontos.

> **Veredito:** veja a tabela. Se o IC95 de phase damping cruzar o baseline,
> o sweet spot não foi validado nestes dados. A ausência de evidência não
> prova que o efeito não existe; prova que 5 trials e 20 pontos de teste
> não bastam para sustentá-lo.