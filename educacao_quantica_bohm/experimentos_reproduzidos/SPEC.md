# SPEC local — Reprodução e melhoria dos experimentos E01–E18 + novo E19

## Objetivo

Reproduzir em simulação os 18 experimentos do livro, com protocolo
estatístico mais forte do que a execução original de 1024 tiros, comparar
com os resultados arquivados e criar um experimento novo (E19 — desigualdade
de Mermin para três qubits).

## Critérios de aceitação

1. E01–E18 executam em `AerSimulator` com 20 sementes × 4096 tiros cada.
2. Cada resultado registra counts agregados, distribuição média, intervalo
   de confiança de 95%, leitura agregada e distância de variação total (TVD)
   contra a distribuição ideal, o JSON simulado arquivado e o JSON real
   arquivado.
3. E19 executa as quatro configurações de medição (XXX, XYY, YXY, YYX),
   calcula `M = E_XXX − E_XYY − E_YXY − E_YYX`, reporta média, erro padrão,
   IC95% e p-valor contra o limite clássico 2.
4. E19 inclui varredura de ruído depolarizante (0; 0,01; 0,02; 0,05) e
   mostra que o valor de M cai com o ruído.
5. Nenhum resultado é atribuído a hardware GJQ/Tiangong; nenhuma submissão
   é feita.
6. MindQuantum não é declarado executado: o ambiente disponível não tem
   MindSpore, o Python é 3.14 e o pacote exige Python <3.13.
7. Testes automatizados passam em modo rápido (2 sementes × 1024 tiros).
8. O relatório é gerado a partir dos JSON reais, não de números inventados.

## Não objetivos

- Submeter jobs ao GJQ ou a qualquer hardware quântico.
- Instalar ou compilar MindQuantum/MindSpore.
- Alterar o catálogo de 18 experimentos do livro.
- Declarar peer review, validade científica externa ou superioridade
  estatística sem um desenho que a sustente.
- Tratar a comparação com o JSON real como reprodução de hardware.

## Entregáveis

- `reproduzir.py` — harness dos E01–E18.
- `e19_mermin.py` — experimento novo.
- `resultados/E01.json` … `E18.json`, `resultados/E19.json`.
- `RESUMO.json` e `RELATORIO.md`.
- `MINDQUANTUM.md` — estado do bloqueio e caminho de portabilidade.
- `tests/test_experimentos_reproduzidos.py` — contratos.
