# SPEC-935-R253 — Atualização do ISBN real do Molambudos

## Objetivo

Substituir o ISBN placeholder do projeto `Molambudos — O Diário do Paciente 1.260` pelo ISBN real informado pelo autor:

`ISBN: 9798189170492`

## Escopo

- Atualizar a macro canônica `\isbn` no `main.tex`.
- Atualizar ocorrências hardcoded em arquivos de capa/contracapa.
- Regenerar o PDF principal.
- Regenerar o ePub reflowable.
- Validar que o ISBN antigo não aparece mais nas fontes principais nem nos artefatos gerados.

## Critérios de aceitação

1. `main.tex` define `\isbn` como `9798189170492`.
2. `contracapa.tex` exibe `ISBN: 9798189170492`.
3. `capa_completa.tex` exibe `ISBN: 9798189170492`.
4. O ISBN antigo `978-65-01-23456-7` não aparece nas fontes principais do projeto.
5. O PDF recompila sem erro.
6. O ePub recompila sem erro e mantém estrutura ZIP válida.
7. O ePub contém `9798189170492` e não contém o ISBN antigo.

## Testes

- Teste RED antes da alteração: verificar que os critérios 1–4 falham no estado atual.
- Teste GREEN após alteração: verificar fontes, PDF extraído e ePub interno.

## Limitações

- A validação confirma presença textual e remoção do placeholder. Não consulta bases externas de ISBN.

## Resultado verificado

- Fontes atualizadas:
  - `main.tex`: `\newcommand{\isbn}{9798189170492}`
  - `contracapa.tex`: `ISBN: 9798189170492`
  - `capa_completa.tex`: `ISBN: 9798189170492`
- Texto de código de barras atualizado para `9 798189 170492` em capa/contracapa.
- Artefatos recompilados:
  - `main.pdf`
  - `contracapa.pdf`
  - `capa_completa.pdf`
  - `main.epub`
  - `Molambudos_O-Diario-do-Paciente-1260_v1.5_2026-07-26.epub`
- Validação final:
  - `GREEN artefatos: ISBN novo validado em fontes, main.pdf e ePub; capas recompiladas; antigo removido dos artefatos atuais`
  - `main.pdf bytes: 9746460`
  - `contracapa.pdf bytes: 3076922`
  - `capa_completa.pdf bytes: 6486148`
  - `main.epub bytes: 8984921`
