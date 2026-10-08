---
spec_id: SPEC-935-R658
title: Gate local de dados e avaliacao para fine-tuning
status: green
component: integrations/finetuning_data.py
test_file: tests/test_r658_finetuning_data.py
---

# SPEC-935-R658 — Dados e avaliacao antes de fine-tuning

## Objetivo

Aplicar as orientacoes de curadoria, deduplicacao e separacao por grupo do livro
Fine-Tuning de LLMs na Pratica a um gate reutilizavel. Este ciclo valida dados
e comparacoes, sem iniciar treinamento ou converter os livros em dataset.

## Contratos

1. Validar registros de pares entrada/resposta com IDs e grupos explicitos,
   recusando vazios e formatos invalidos; reportar diagnosticos sem ecoar dados.
2. Deduplicar conteudo normalizado e particionar de forma deterministica por
   grupo, preservando grupos inteiros e detectando conflitos que vazariam entre
   treino, validacao e teste. Nao prometer tres splits com grupos insuficientes.
3. Manter rastreabilidade por hashes/IDs e seed. Validacao bloqueia conjuntos
   insuficientes; nao renomear falta de evidencias como sucesso.
4. Gate de avaliacao compara baseline e candidato no MESMO conjunto congelado,
   com metrica, direcao e limiar explicitos. Recusar NaN, infinito, booleans,
   amostras ou hashes divergentes e ausencia de resultados reais.
5. Testes comportamentais precedem implementacao, cobrindo vazamento, conflitos,
   independencia da ordem e rejeicao de evidencias incompletas.
6. Expor CLI local pelo orquestrador e documentar formato e limites. Exemplos
   sinteticos nao constituem evidencia de treinamento ou ganho de modelo.

## Aceitacao

- Tests R658 passam e tornam erros de dados acionaveis.
- Nenhum modelo ou dado clinico enviado a servicos externos.
- Ciclo registrado sem score cognitivo ou alegacao de fine-tuning executado.

## Critérios de aceitação executáveis

- `R658-SPLITS` — Deduplicação e componentes transitivos preservam grupos sem vazamento.
- `R658-REPRODUCIBILITY` — Seed e hashes permanecem estáveis sob reordenação dos registros.
- `R658-EVALUATION` — Comparação recusa protocolos incompatíveis, valores inválidos e ganho insuficiente.

O test_file executa os casos de preparação e comparação. Aceitação dos números
fornecidos continua restrita a reported_results_only; não é prova de inferência.
