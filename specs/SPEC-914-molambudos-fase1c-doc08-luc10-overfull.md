# SPEC-914 — Molambudos Fase 1C: reduzir didatismo de DOC-08/LUC-10 e corrigir overfull remanescente

## Objetivo
Executar a próxima passada editorial após a Fase 1B, atacando três pontos pendentes: o excesso didático/metaficcional de `DOC-08`, o laudo excessivamente explícito de `LUC-10` e os dois `overfull hbox` remanescentes em `DOC-18` e `CONT-07`.

## Escopo
- Projeto: `projetos/molambudos/Molambudos_VictoriaRegia`.
- Fragmentos-alvo principais:
  - `fragmentos/doc/DOC-08.tex`;
  - `fragmentos/luc/LUC-10.tex`;
  - `fragmentos/doc/DOC-18.tex`;
  - `fragmentos/cont/CONT-07.tex`.
- Manter o tom de horror psicológico e contaminação narrativa, mas por sugestão documental, não por explicação direta.
- Preservar os links finais de leitura de todos os fragmentos alterados.

## Critérios de aceitação
1. `DOC-08` deve deixar de funcionar como checklist explícito para o leitor e passar a soar como parecer retrospectivo com anotações marginais/anomalias de arquivo.
2. `DOC-08` não deve afirmar diretamente que o diagnóstico é do leitor; a captura deve ser sugerida por campos em branco, lacunas, rasuras ou alterações de formulário.
3. `LUC-10` deve parecer um registro profissional deteriorado/autoencaminhamento, não uma confirmação literal de criatura ou parasita narrativo.
4. Expressões excessivamente explícitas devem ser removidas ou atenuadas nos alvos: `PARA O LEITOR`, `Você está abrigando`, `A criatura não é um delírio`, `parasita narrativo`, `Para você`, `Próxima: você`.
5. `DOC-18` e `CONT-07` devem ser ajustados para reduzir/eliminar os `overfull hbox` reportados no `main.log` sem alterar a função narrativa.
6. O PDF deve compilar em duas passagens sem erro fatal, sem destinos duplicados e sem font warnings.
7. O relatório da Fase 1C deve registrar alterações, métricas finais e pendências.

## Verificação
- Leitura manual dos quatro fragmentos alterados.
- Busca textual pelas expressões explícitas listadas no critério 4.
- Compilação dupla: `pdflatex -interaction=nonstopmode main.tex`.
- Contagem de `LaTeX Error`, `Fatal error`, `Overfull \hbox`, `Overfull \vbox`, `destination with the same identifier` e `Font Warning` em `main.log`.
