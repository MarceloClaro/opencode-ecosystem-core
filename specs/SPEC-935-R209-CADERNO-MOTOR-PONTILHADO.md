# SPEC-935-R209 — Caderno Motor de Escrita Cursiva Pontilhada

**Status:** EM EXECUÇÃO
**Ciclo de evolução:** R209 → registro R511 (evolution registry)
**Escopo:** `livro-alfabetizacao/CadernoMotor/` (caderno independente, pauta dupla,
letras pontilhadas para treino motor), usando `fontes/Mestra4(DoblePautaPuntejada).TTF`
e `fontes/Mestra2(MeMimaPuntejada).TTF`.

## Contexto

O usuário solicitou: **"adicione as fontes cursivas e atividades motoras com as
letras cursivas pontilhadas para treino motor"**. Verificação técnica:

- `Mestra2(MeMimaPuntejada).TTF` e `Mestra4(DoblePautaPuntejada).TTF` (Downloads):
  266 glyphs, acentos PT confirmados, **fsType=0 (sem restrição de incorporação)**. ✓
- `SchoolScriptDashed.ttf`: **fsType=2 (restrição de incorporação)** → fora (decisão
  do usuário mantida; verificada por fontTools).
- Fonte cursiva contínua já integrada (R208): `irineu cursivo escolar.ttf`.

## Objetivo

Gerar um **caderno independente** (112 p. alvo, ~38 folhas) de treino motor com:
- páginas de pauta dupla (linhas guia) desenhadas em TikZ;
- letras pontilhadas (Mestra4, caixa alta + baixa) para contornar;
- espaço de treino com linhas guia (sem pontuação clínica);
- páginas de ligações (aa, ab, ...) e palavras-modelo pontilhadas (Mestra2);
- registro pedagógico opcional por página (data/observação do mediador), **sem
  nota diagnóstica** (conforme R201.4/parte6 do V1).

## Critérios de aceitação (gate SDD)

- [x] AC1: `fontes/` contém Mestra2 e Mestra4 (com README atualizado) —
      verificadas: 266 glyphs, acentos PT, fsType=0.
- [x] AC2: `CadernoMotor/main.tex` gerado por script reproduzível
      (`gerar_caderno.py`): 26 folhas de letras (A–Z), 6 de ligações, 6 de
      palavras → 41 páginas compiladas.
- [x] AC3: compilação `xelatex -interaction=nonstopmode main.tex` 2× → exit 0;
      0 "Missing character"; **0 Overfull** (após correção de parágrafo da
      macro `\pauta`).
- [x] AC4: conteúdo das FICHAS sem menção a transtorno/TDAH/dislexia/CID/nota
      clínica (ocorrências de "diagnóstico" apenas em avisos legais do
      preâmbulo e capa).
- [x] AC5: PDF `Caderno_Motor_Pontilhado_v1.0.pdf` entregue em
      `/mnt/c/Users/marce/Downloads/Alfabetizar_Bem/` (41 páginas).
- [x] AC6: ciclo R511 registrado no EvolutionRegistry com lições (registro
      junto ao R512).

## Restrições

- Sem SchoolScriptDashed (fsType=2) e sem Irineu Brasil Infantil A (comercial).
- Sem conteúdo clínico/diagnóstico; observação pedagógica apenas.
- Caderno independente (não altera a estrutura dos Volumes 1–5).