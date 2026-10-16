# Plano R911 — Atlas de arquiteturas do livro

Objetivo: entregar orientação mental, estrutura e fluxo junto aos capítulos e uma
visão global navegável. Stack: LaTeX/TikZ, Python, Graphviz, Mermaid, Lean 4 fixado.
Spec: specs/SPEC-935-R911-atlas-arquiteturas-livro.md.

1. Escrever teste RED das 18 tríades e da conservação dos nós/imports do snapshot.
2. Dois editores leem código e escrevem dados curados em arquivos distintos;
   um auditor independente confere fontes/fluxos. Perfis ativados pelo primário.
3. Gerar TikZ/legendas/referências por capítulo e mapas globais com fonte reproduzível.
4. Inserir no livro, criar índice e legenda geral, regenerar inventários.
5. Revisar semântica, renderizar todas as novas figuras, corrigir layout e compilar.
6. Congelar fontes, executar gates/Lean e conferir hashes; registrar ciclo e publicar.

Foco: não confundir imports com execução; não duplicar coordenadores; representar
ramos de falha; não mostrar chamada remota como local; preservar nós isolados;
não imprimir rótulos minúsculos; não deixar figuras somente em arquivos externos.
