# SPEC-935-R910 — Deduções locais e rastreabilidade Lean no livro

Status: implementação editorial registrada; resultados físicos e limites no manifesto docs/verification-book-r910.json.

## Objetivo e contrato

Explicitar junto às deduções de cada capítulo do inventário R908 os enunciados,
hipóteses, lemas de apoio, passos matemáticos e correspondência nominal com Lean 4.
Os 158 teoremas existentes não são substituídos por rótulos de comprovação genérica.
Cada par família formal/fonte da matriz recebe ao menos um bloco local identificado.
Quando uma família reaparecer em outra dedução substantiva, explicitar sua aplicação.

O ambiente `formalizacao` recebe identificação da família e título. Seu corpo contém
Enunciado, Hipóteses, Lemas e dedução, Lean 4, Axiomas e alcance. `\leanref{Nome}`
identifica uma declaração real auditada; o escopo não excede seu enunciado. Propriedades
derivadas de probabilidade deixam de ser chamadas axiomas. Não criar axiomas locais.
As dependências fundamentais de cada declaração serão publicadas em anotações nominais geradas
do recibo da compilação real, separadas das hipóteses empíricas do modelo. Não inventar
lemas se a prova é diretamente aritmética ou definicional; nomear a regra usada.

F27 (observações) não recebe bloco formal nem teorema de ocorrência. Capítulos sem
fórmula nova continuam narrativos, com remissão explícita quando pertinente; não se
adicionam provas artificiais para preencher capítulos. Preservar a nota do autor,
citações, manuscrito aberto e alterações alheias. Editar geradores dos módulos gerados.

## Aceitação e evidências

- Teste editorial inicialmente RED por ausência dos blocos, separado de prova formal.
- Validador de correspondência rejeita família sem bloco local, nome inexistente,
  hipótese ausente, família empírica promovida e referência não auditada.
- Auditoria humana assistida de semântica texto/prova; sem métrica de qualidade epistêmica.
- Lean 4/Mathlib fixados, todas as provas e controles negativos reexecutados.
- Livro existente compilado, check.py e gates R617–R620/R814/R901/R907/R908/R910
  aplicáveis; coordenadas e amostra visual de cada capítulo alterado.
- Recibos com hashes atuais, registro R910 e commit/push na branch já autorizada.
- Não declarar validação externa, equivalência com runtime Python ou segurança IEEE-754.
